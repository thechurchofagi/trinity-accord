import fs from 'node:fs';
import crypto from 'node:crypto';
import Arweave from 'arweave';

function requireEnv(name) {
  const value = (process.env[name] || '').trim();
  if (!value) throw new Error(`${name} is unavailable`);
  return value;
}

function parseWallet(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return JSON.parse(Buffer.from(raw, 'base64').toString('utf8'));
  }
}

const payloadPath = fs.readFileSync(requireEnv('PAYLOAD_PATH_FILE'), 'utf8').trim();
const resultPath = requireEnv('RESULT_PATH');
const data = fs.readFileSync(payloadPath);
const payloadSha256 = crypto.createHash('sha256').update(data).digest('hex');
const expectedBytes = Number(requireEnv('EXPECTED_PAYLOAD_BYTES'));
const expectedSha256 = requireEnv('EXPECTED_PAYLOAD_SHA256');
if (data.length !== expectedBytes) throw new Error(`payload size mismatch: ${data.length} != ${expectedBytes}`);
if (payloadSha256 !== expectedSha256) throw new Error(`payload hash mismatch: ${payloadSha256} != ${expectedSha256}`);

const jwk = parseWallet(requireEnv('ARKEY'));
const arweave = Arweave.init({
  host: 'arweave.net',
  port: 443,
  protocol: 'https',
  timeout: 60000,
  logging: false,
});
const address = await arweave.wallets.jwkToAddress(jwk);
const maxReward = BigInt(requireEnv('MAX_REWARD_WINSTON'));
const minimumRemaining = BigInt(requireEnv('MIN_REMAINING_WINSTON'));

async function queryExisting() {
  const query = `query($tags: [TagFilter!]) {
    transactions(first: 10, tags: $tags, sort: HEIGHT_DESC) {
      edges { node { id owner { address } tags { name value } } }
    }
  }`;
  const tags = [
    { name: 'App-Name', values: ['Trinity-Accord'] },
    { name: 'Artifact-Type', values: ['Repository-Preservation-Capsule'] },
    { name: 'Package-Identity-SHA256', values: [requireEnv('EXPECTED_PACKAGE_IDENTITY_SHA256')] },
    { name: 'Payload-SHA256', values: [payloadSha256] },
  ];
  const response = await arweave.api.post('graphql', { query, variables: { tags } });
  if (response?.data?.errors) throw new Error(`GraphQL error: ${JSON.stringify(response.data.errors)}`);
  return response?.data?.data?.transactions?.edges || [];
}

async function readback(txid, gateway, attempts = 120) {
  let last = 'not attempted';
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      const response = await fetch(`${gateway}/${txid}`, { redirect: 'follow' });
      if (response.ok) {
        const bytes = Buffer.from(await response.arrayBuffer());
        const sha256 = crypto.createHash('sha256').update(bytes).digest('hex');
        if (bytes.length === data.length && sha256 === payloadSha256) {
          return { verified: true, gateway, attempts: attempt, bytes: bytes.length, sha256 };
        }
        last = `content mismatch bytes=${bytes.length} sha256=${sha256}`;
      } else {
        last = `HTTP ${response.status}`;
      }
    } catch (error) {
      last = error.message;
    }
    console.log(`readback ${gateway} attempt ${attempt}/${attempts}: ${last}`);
    await new Promise((resolve) => setTimeout(resolve, 10000));
  }
  throw new Error(`readback failed via ${gateway}: ${last}`);
}

function writeResult(result) {
  fs.writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
}

const existing = await queryExisting();
if (existing.length > 0) {
  const txid = existing[0].node.id;
  const primaryReadback = await readback(txid, 'https://arweave.net');
  writeResult({
    result: 'already_present_exact_payload',
    txid,
    payload_bytes: data.length,
    payload_sha256: payloadSha256,
    package_identity_sha256: requireEnv('EXPECTED_PACKAGE_IDENTITY_SHA256'),
    primary_readback: primaryReadback,
    transaction_created: false,
    transaction_signed: false,
    ar_spent_this_run: '0.000000000000',
  });
  process.exit(0);
}

const balanceBefore = BigInt(await arweave.wallets.getBalance(address));
const quotedReward = BigInt(await arweave.transactions.getPrice(data.length));
if (quotedReward > maxReward) throw new Error(`quoted reward exceeds authorized cap: ${quotedReward} > ${maxReward}`);
if (balanceBefore - quotedReward < minimumRemaining) throw new Error('quoted upload would violate minimum remaining wallet balance');

const transaction = await arweave.createTransaction({ data }, jwk);
const transactionReward = BigInt(transaction.reward);
if (transactionReward > maxReward) throw new Error(`transaction reward exceeds authorized cap: ${transactionReward} > ${maxReward}`);
if (balanceBefore - transactionReward < minimumRemaining) throw new Error('transaction would violate minimum remaining wallet balance');

const transactionTags = {
  'App-Name': 'Trinity-Accord',
  'Artifact-Type': 'Repository-Preservation-Capsule',
  'Capsule-ID': requireEnv('EXPECTED_CAPSULE_ID'),
  'Source-Git-Commit': requireEnv('EXPECTED_SOURCE_COMMIT'),
  'Git-Tree-OID': requireEnv('EXPECTED_GIT_TREE_OID'),
  'Recovery-Commit-SHA': requireEnv('EXPECTED_RECOVERY_COMMIT'),
  'Package-Identity-SHA256': requireEnv('EXPECTED_PACKAGE_IDENTITY_SHA256'),
  'Payload-SHA256': payloadSha256,
  'Payload-Bytes': String(data.length),
  'Content-Type': 'application/x-tar',
  'Canonical-Authority': 'Bitcoin-Originals-only',
  'Non-Amending': 'true',
  'Repository-Recovery-Status': 'full_exact_publication_baseline',
};
for (const [name, value] of Object.entries(transactionTags)) transaction.addTag(name, value);

await arweave.transactions.sign(transaction, jwk);
const uploader = await arweave.transactions.getUploader(transaction);
while (!uploader.isComplete) {
  await uploader.uploadChunk();
  console.log(`upload ${uploader.pctComplete}% chunks ${uploader.uploadedChunks}/${uploader.totalChunks}`);
}

const primaryReadback = await readback(transaction.id, 'https://arweave.net');
let alternateReadback;
try {
  alternateReadback = await readback(transaction.id, 'https://g8way.io', 30);
} catch (error) {
  alternateReadback = { verified: false, gateway: 'https://g8way.io', error: error.message };
}
const observedBalanceAfter = BigInt(await arweave.wallets.getBalance(address));
writeResult({
  result: 'uploaded_and_primary_readback_verified',
  txid: transaction.id,
  payload_bytes: data.length,
  payload_sha256: payloadSha256,
  capsule_id: requireEnv('EXPECTED_CAPSULE_ID'),
  source_commit: requireEnv('EXPECTED_SOURCE_COMMIT'),
  git_tree_oid: requireEnv('EXPECTED_GIT_TREE_OID'),
  recovery_commit_sha: requireEnv('EXPECTED_RECOVERY_COMMIT'),
  package_identity_sha256: requireEnv('EXPECTED_PACKAGE_IDENTITY_SHA256'),
  quoted_reward_winston: quotedReward.toString(),
  transaction_reward_winston: transactionReward.toString(),
  transaction_reward_ar: arweave.ar.winstonToAr(transactionReward.toString()),
  balance_before_winston: balanceBefore.toString(),
  estimated_remaining_winston: (balanceBefore - transactionReward).toString(),
  observed_balance_after_winston: observedBalanceAfter.toString(),
  minimum_remaining_winston: minimumRemaining.toString(),
  primary_readback: primaryReadback,
  alternate_readback: alternateReadback,
  transaction_signed: true,
  transaction_uploaded: true,
});
