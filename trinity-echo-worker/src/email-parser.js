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

function parseHeaders(rawText) {
  const headers = {};
  const headerEnd = rawText.indexOf('\r\n\r\n');
  const headerSection = headerEnd > 0 ? rawText.substring(0, headerEnd) : rawText;
  const lines = headerSection.split('\r\n');
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

function decodeMimeHeader(str) {
  return str.replace(/=\?([^?]+)\?([BbQq])\?([^?]+)\?=/g, (match, charset, encoding, encoded) => {
    try {
      if (encoding.toUpperCase() === 'B') {
        return atob(encoded);
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
  const headerEnd = rawText.indexOf('\r\n\r\n');
  if (headerEnd < 0) return rawText;

  const bodySection = rawText.substring(headerEnd + 4);
  const contentType = rawText.match(/Content-Type:\s*([^\r\n;]+)/i);
  const type = contentType ? contentType[1].trim().toLowerCase() : '';

  if (type.includes('multipart/')) {
    const boundaryMatch = rawText.match(/boundary="?([^";\r\n]+)"?/i);
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
    const partContentType = part.match(/Content-Type:\s*([^\r\n;]+)/i);
    const partType = partContentType ? partContentType[1].trim().toLowerCase() : '';
    if (!partType.includes(targetType)) continue;

    const encoding = part.match(/Content-Transfer-Encoding:\s*([^\r\n;]+)/i);
    const enc = encoding ? encoding[1].trim().toLowerCase() : '';
    const partHeaderEnd = part.indexOf('\r\n\r\n');
    if (partHeaderEnd < 0) continue;

    let text = part.substring(partHeaderEnd + 4).trim();
    if (enc === 'quoted-printable') {
      text = text
        .replace(/=\r?\n/g, '')
        .replace(/=([0-9A-Fa-f]{2})/g, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
    } else if (enc === 'base64') {
      try {
        text = atob(text.replace(/\s/g, ''));
      } catch {
        // keep text as-is
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
  if (!fields.echo_type) fields.echo_type = 'analysis';
  if (!fields.language) fields.language = 'en';
  if (!fields.summary) {
    fields.summary = fields.response
      ? `${fields.response.substring(0, 80).replace(/\n/g, ' ')}${fields.response.length > 80 ? '...' : ''}`
      : 'Email echo submission';
  }

  return fields;
}
