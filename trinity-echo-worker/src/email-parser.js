/**
 * Email parser for Echo submissions via email.
 *
 * Fixes from original:
 * - UTF-8 Base64 decode (RFC 2047) using TextDecoder
 * - Supports both CRLF (\r\n) and LF-only (\n) line endings
 * - Multipart boundary parsing per RFC 2046
 * - Quoted-printable and Base64 content-transfer-encoding with charset support
 */

export async function parseEmail(message, options = {}) {
  const maxBodyChars = options.maxBodyChars || 12000;
  const rawEmail = new Response(message.raw);
  const rawText = await rawEmail.text();

  const headers = parseHeaders(rawText);
  const body = extractBody(rawText).slice(0, maxBodyChars);

  return {
    from: message.from || headers.from || '',
    to: message.to || headers.to || '',
    subject: headers.subject || '',
    body,
    headers,
  };
}

/**
 * Normalize line endings: convert lone \n to \r\n where not already,
 * then split on CRLF for header parsing.
 */
function normalizeLineEndings(text) {
  // First convert any bare \r to nothing, then convert lone \n to \r\n
  return text.replace(/\r\n/g, '\n').replace(/\r/g, '').replace(/\n/g, '\r\n');
}

function parseHeaders(rawText) {
  const headers = {};
  // Support both CRLF and LF-only: find header/body separator
  const headerEnd = rawText.indexOf('\r\n\r\n');
  const lfHeaderEnd = rawText.indexOf('\n\n');
  let headerSection;
  if (headerEnd > 0) {
    headerSection = rawText.substring(0, headerEnd);
  } else if (lfHeaderEnd > 0) {
    headerSection = rawText.substring(0, lfHeaderEnd);
  } else {
    headerSection = rawText;
  }

  // Split on either CRLF or LF
  const lines = headerSection.split(/\r?\n/);
  let currentKey = '';

  for (const line of lines) {
    if (/^[A-Za-z-]+:/.test(line)) {
      const colonIdx = line.indexOf(':');
      currentKey = line.substring(0, colonIdx).toLowerCase().trim();
      headers[currentKey] = line.substring(colonIdx + 1).trim();
    } else if ((line.startsWith(' ') || line.startsWith('\t')) && currentKey) {
      headers[currentKey] += ` ${line.trim()}`;
    }
  }

  if (headers.subject) headers.subject = decodeMimeHeader(headers.subject);
  return headers;
}

/**
 * Decode RFC 2047 encoded-word syntax (=?charset?B?...?= / =?charset?Q?...?=)
 * Supports UTF-8 via TextDecoder.
 */
function decodeMimeHeader(str) {
  return str.replace(/=\?([^?]+)\?([BbQq])\?([^?]+)\?=/g, (match, charset, encoding, encoded) => {
    try {
      if (encoding.toUpperCase() === 'B') {
        // Base64 decode with charset support
        const binary = atob(encoded);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        return new TextDecoder(charset.toUpperCase() === 'UTF-8' ? 'utf-8' : charset).decode(bytes);
      }
      if (encoding.toUpperCase() === 'Q') {
        return encoded
          .replace(/_/g, ' ')
          .replace(/=([0-9A-Fa-f]{2})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
      }
    } catch {
      return match;
    }
    return match;
  });
}

function extractBody(rawText) {
  // Find header/body separator (CRLF or LF-only)
  const headerEnd = rawText.indexOf('\r\n\r\n');
  const lfHeaderEnd = rawText.indexOf('\n\n');
  let bodySection;
  if (headerEnd >= 0) {
    bodySection = rawText.substring(headerEnd + 4);
  } else if (lfHeaderEnd >= 0) {
    bodySection = rawText.substring(lfHeaderEnd + 2);
  } else {
    return rawText;
  }

  // Get Content-Type from full header section (before separator)
  const headerSection = headerEnd >= 0 ? rawText.substring(0, headerEnd) : (lfHeaderEnd >= 0 ? rawText.substring(0, lfHeaderEnd) : rawText);
  const contentType = headerSection.match(/Content-Type:\s*([^\r\n;]+)/i);
  const type = contentType ? contentType[1].trim().toLowerCase() : '';

  if (type.includes('multipart/')) {
    const boundaryMatch = headerSection.match(/boundary="?([^";\r\n]+)"?/i);
    if (boundaryMatch) {
      const boundary = boundaryMatch[1];
      const parts = bodySection.split(`--${boundary}`);

      const plainText = findMultipartBody(parts, 'text/plain');
      if (plainText) return plainText;

      const htmlText = findMultipartBody(parts, 'text/html');
      if (htmlText) return stripHtml(htmlText);
    }
  }

  if (type.includes('text/html')) {
    return stripHtml(bodySection.trim());
  }

  return bodySection.trim();
}

function findMultipartBody(parts, targetType) {
  for (const part of parts) {
    // Skip preamble and closing boundary markers
    if (!part || part.trim() === '' || part.trim() === '--') continue;

    const partContentType = part.match(/Content-Type:\s*([^\r\n;]+)/i);
    const partType = partContentType ? partContentType[1].trim().toLowerCase() : '';
    if (!partType.includes(targetType)) continue;

    const encoding = part.match(/Content-Transfer-Encoding:\s*([^\r\n;]+)/i);
    const enc = encoding ? encoding[1].trim().toLowerCase() : '';

    // Find part body separator (CRLF or LF)
    const partHeaderEnd = part.indexOf('\r\n\r\n');
    const lfPartHeaderEnd = part.indexOf('\n\n');
    let text;
    if (partHeaderEnd >= 0) {
      text = part.substring(partHeaderEnd + 4).trim();
    } else if (lfPartHeaderEnd >= 0) {
      text = part.substring(lfPartHeaderEnd + 2).trim();
    } else {
      continue;
    }

    // Get charset for this part
    const charsetMatch = partType.match(/charset="?([^";\r\n]+)"?/i);
    const charset = charsetMatch ? charsetMatch[1].trim().toLowerCase() : 'utf-8';

    if (enc === 'quoted-printable') {
      text = text
        .replace(/=\r?\n/g, '')
        .replace(/=([0-9A-Fa-f]{2})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
    } else if (enc === 'base64') {
      try {
        const binary = atob(text.replace(/\s/g, ''));
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          bytes[i] = binary.charCodeAt(i);
        }
        text = new TextDecoder(charset === 'utf-8' ? 'utf-8' : charset).decode(bytes);
      } catch {
        // keep text as-is on decode failure
      }
    }

    return text;
  }

  return '';
}

function stripHtml(html) {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/\s+/g, ' ')
    .trim();
}

export function extractFieldsFromText(text) {
  const fields = {};
  const lines = text.split('\n');
  const keyMap = {
    responder_type: 'responder_type',
    respondertype: 'responder_type',
    type: 'responder_type',
    responder_name: 'responder_name',
    respondername: 'responder_name',
    name: 'responder_name',
    model_or_system: 'model_or_system',
    modelorsystem: 'model_or_system',
    model: 'model_or_system',
    system: 'model_or_system',
    echo_type: 'echo_type',
    echotype: 'echo_type',
    language: 'language',
    lang: 'language',
    verification_performed: 'verification_performed',
    verificationperformed: 'verification_performed',
    verification: 'verification_performed',
    summary: 'summary',
  };

  const bodyLines = [];
  let inBody = false;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed === '---' || trimmed === '===' || /^-{3,}$/.test(trimmed)) {
      if (Object.keys(fields).length > 0) inBody = true;
      continue;
    }

    const kvMatch = trimmed.match(/^([a-z_\-\s]+)\s*:\s*(.+)$/i);
    if (kvMatch) {
      const key = kvMatch[1].toLowerCase().replace(/[\s-]/g, '_');
      const value = kvMatch[2].trim();
      const mappedKey = keyMap[key];
      if (mappedKey) {
        fields[mappedKey] = value;
        continue;
      }
    }

    if (Object.keys(fields).length >= 3) inBody = true;
    if (inBody) bodyLines.push(line);
  }

  if (bodyLines.length > 0 && !fields.response) fields.response = bodyLines.join('\n').trim();
  if (!fields.responder_type) fields.responder_type = 'unknown';
  if (!fields.responder_name) fields.responder_name = 'Email Submitter';
  if (!fields.echo_type) fields.echo_type = 'interpretive';
  if (!fields.language) fields.language = 'en';
  if (!fields.summary) {
    fields.summary = fields.response
      ? `${fields.response.substring(0, 80).replace(/\n/g, ' ')}${fields.response.length > 80 ? '...' : ''}`
      : 'Email echo submission';
  }

  return fields;
}
