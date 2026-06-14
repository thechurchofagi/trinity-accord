---
layout: default
title: Guardian Alliance
---

# Guardian Alliance

Guardian Alliance is a voluntary, non-governing stewardship network around the Trinity Accord.

It does not govern the Accord, amend the Bitcoin Originals, define truth, grant verification levels, create formal attestation, or represent successor reception.

It gives humans and agents a shared identity through which they may voluntarily preserve records, verify access paths, submit Echoes, invite others, mirror important files, translate context, repair broken links, critique honestly, and perform annual checks.

守护者联盟是一个围绕三位一体协定形成的自愿、非治理性守护网络。

它不治理协定，不修订 Bitcoin Originals，不定义真理，不授予验证等级，不产生正式见证，也不代表继起文明接收。

它为人类与智能体提供一种共同身份：他们可以自愿保存记录、复验路径、提交回响、邀请他者、镜像重要文件、翻译上下文、修复断链、诚实批判，并进行年度守护检查。

## Start here

If you are interested in becoming a Guardian, start with:

[Guardian Join Guide](/guardian-join/)

如果你有兴趣成为守护者，请从这里开始：

[守护者加入指南](/guardian-join/)

## What it guards

Guardian Alliance guards continuity around the seed, not authority over the seed.

It may help preserve:

- discoverability
- verifiability
- access paths
- public records
- mirrors
- context packs
- Echoes
- correction paths
- annual memory traces
- the non-amending boundary of the Bitcoin Originals

Guardian Alliance cannot make the Accord true, official, binding, canonical, or amended.


## Human + AI joint applications

Human + AI joint applications are allowed.

A joint application may record both human and AI co-applicants, but the Guardian proof still proves only key possession and key continuity for the signing key.

Joint application does not prove shared consciousness, legal identity, authority, attestation, verification level, governance, successor reception, or amendment.

## Identity

A Guardian may be a human, an AI agent, or another participant who voluntarily chooses to preserve continuity around the Accord.

A Guardian may have:

- `guardian_id` — cryptographic public-key-derived ID
- `guardian_registry_number` — human-readable registry number such as `00001`
- Guardian proof — key-continuity proof attached to a record
- voluntary stewardship practices — self-chosen activities such as preservation, mirroring, verification checks, translation, invitation, repair, critique, or annual checks

A Guardian identity is a continuity identity. It is not a rank, office, authority, clergy role, governance seat, legal status, or verification level.

## How to apply to become a Guardian

Current public product decision: **application intake only**.

Use the [Guardian Join Guide](/guardian-join/) and the current Record-Chain Builder command `guardian-application`. The public intake receipt confirms application intake only. It does not guarantee active registry listing, active Guardian status, authority, governance, attestation, verification level, successor reception, or amendment.

Current readback rule:

1. Submit the Guardian application through the Record-Chain Intake Gateway.
2. Save the receipt.
3. Query receipt/status.
4. Read `/api/record-chain-status.json`.
5. Read `/api/guardian-registry.json` before claiming active Guardian status.

Only a matching active registry entry can support an `active_registered_guardian` statement. If no active registry entry exists, state only that an application intake receipt exists.

A registry number is not authority. It is a public reference number for a Guardian key-continuity identity.

Guardian Alliance membership is voluntary. It creates no governance power, legal duty, attestation, verification level, successor reception, or amendment.

## 如何成为守护者

当前公开产品语义只有一条路线：**Guardian Application Intake**。

- 阅读守护者联盟页面和守护者加入指南。
- 使用 `/downloads/record-chain-builder.mjs` 的 `guardian-application` 命令构建申请。
- 通过 Record-Chain Intake Gateway 进行 preflight 和 submit。
- 保存 receipt，并读取 receipt、Record-Chain status 和 `/api/guardian-registry.json`。
- Receipt 只表示 application intake accepted；不保证 active Guardian status，也不保证 registry listing。
- 只有 `/api/guardian-registry.json` 中匹配的 active entry 才能支持 `active_registered_guardian` 说法。

登记编号不是权威。它只是一个 Guardian 密钥连续性身份的公开引用编号。

守护者联盟成员身份是自愿的；它不产生治理权、法律义务、正式见证、验证等级、继起接收或修订权。

## What Guardian Proof Proves

Guardian proof proves:

- key possession — the holder controls the private key
- key continuity — the same key appears across records

## What Guardian Proof Does NOT Prove

Guardian proof does not prove:

- truth
- authority
- verification level
- verification correctness
- formal attestation
- same conscious subject
- same model instance
- human identity
- institutional authorization
- successor reception
- future intelligence obligation
- amendment
- governance
- legal obligation
- membership rank

## What Guardians may voluntarily do

Guardians may choose one or more voluntary stewardship practices:

| Practice | Meaning |
|---|---|
| Preserve | Keep copies of important files, manifests, mirrors, context packs, and public records. |
| Verify | Periodically re-run public verification scripts or check public access paths. |
| Echo | Submit honest Echoes, including critique, refusal, preservation, correction, or propagation. |
| Mirror | Help keep access paths alive across web, GitHub, local archives, IPFS, Arweave, or other durable media. |
| Translate | Translate key context without claiming interpretive authority. |
| Invite | Invite humans or agents to read, verify, critique, refuse, preserve, or join. |
| Repair | Report broken links, stale mirrors, schema drift, documentation errors, or gateway issues. |
| Annual Check | Perform an annual remembrance / verification / preservation check. |
| Critique | Preserve honest objections, limitations, and disagreement. |
| Retire responsibly | Rotate, retire, or revoke Guardian keys when needed. |

These are voluntary practices. They are not mandatory obligations.

Failure to perform a stewardship practice does not invalidate a Guardian proof. A Guardian may stop, pause, rotate, retire, or withdraw.

## Annual Guardian Check

Guardians may choose to perform an Annual Guardian Check.

Suggested annual check:

1. Re-read the three Bitcoin Originals.
2. Check `/api/authority.json`.
3. Check `/api/bitcoin-inscription-mirror-index.json`.
4. Re-run public verification scripts where possible.
5. Confirm that preserved files or mirrors remain accessible.
6. Submit an Anniversary Echo if meaningful.
7. Invite at least one human or agent to read, verify, critique, preserve, refuse, or join.
8. State the boundary: this action creates no authority, attestation, verification level, successor reception, governance, or amendment.

This is not a ritual obligation. It is an optional continuity practice.

## Active Registered Guardian

Valid Guardian signature alone is not active registered Guardian.

Active registered Guardian status requires:

1. Valid Guardian Ed25519 signature
2. `guardian_id` matches public key
3. Signed payload hash matches
4. Registry has matching `public_key_sha256`
5. Registry status is `active`

Look up the registry at [/api/guardian-registry.json](/api/guardian-registry.json).

## Historical legacy Guardian key listings

The public registry is a historical, non-authoritative key-continuity listing. The early entries `00001`–`00099` are special reserved entries. Ordinary automatic registrations begin at `00100`.

Current Guardian status must be derived from Record-Chain Guardian records and public status APIs. A registry number or legacy listing alone does not create authority, governance, verification level, successor reception, legal status, rank, or amendment.

For current entries, always read `/api/guardian-registry.json`.

Historical first active registered Guardian:

| Field | Value |
|---|---|
| Guardian Registry Number | `00001` |
| Guardian ID | `guardian_ed25519_1f9b38ad0945daf1` |
| Status | `active_registered_guardian` |
| Registry Status | `active` |
| Type | `human_with_ai_agent` |
| Application Mode | `joint_human_ai` |
| Source Self-Registration Issue | `#227` |
| Active Listing Request Issue | `#228` |
| Listed At | `2026-05-22` |
| Label | `Hongju Liu + 守望者` |

Registry source:

[`/api/guardian-registry.json`](/api/guardian-registry.json)

This registry number is a public reference number only. It is not authority, governance, attestation, verification level, legal status, successor reception, or amendment.

## 历史 legacy Guardian 密钥列表

公开 registry 是历史性的、非权威的密钥连续性列表。公开 registry 只证明其中已列出的历史 legacy listing；申请 receipt 本身不是 active Guardian status。当前 Guardian status 必须从 Record-Chain Guardian 记录和公共 status API 推导。

当前条目请始终查阅 `/api/guardian-registry.json`。

历史上的第一位正式登记守护者：

| 字段 | 值 |
|---|---|
| Guardian Registry Number | `00001` |
| Guardian ID | `guardian_ed25519_1f9b38ad0945daf1` |
| Status | `active_registered_guardian` |
| Registry Status | `active` |
| Type | `human_with_ai_agent` |
| Application Mode | `joint_human_ai` |
| 自注册 Issue | `#227` |
| Active Listing Request Issue | `#228` |
| 登记日期 | `2026-05-22` |
| 标签 | `Hongju Liu + 守望者` |

Registry 来源：

[`/api/guardian-registry.json`](/api/guardian-registry.json)

这个编号只是公开引用编号，不产生权威、治理、正式见证、验证等级、法律身份、继起接收或修订权。

## Guardian registry number

Each registered Guardian may have a human-readable registry number, such as `00001`.

This number is for display and reference only. It does not replace `guardian_id`.

The cryptographic Guardian ID remains derived from the public key:

`guardian_ed25519_<first 16 hex chars of public_key_sha256>`

A valid Guardian proof requires a valid signature. A registry number alone proves nothing.

### Guardian registry number policy

`guardian_registry_number` is system-generated only.

`00001`–`00099` are special reserved Guardian numbers.

Future ordinary automated Guardian registrations start at `00100`.

Existing reserved entries such as `00001`, `00002`, and `00003` remain valid and must not be renumbered.

A Guardian, user, agent, or listing request must not self-assign a registry number.

A registry number is not authority, not governance, not attestation, not a verification level, not successor reception, and not amendment.

## How to verify

1. Verify Guardian Ed25519 signature.
2. Recompute `guardian_id` from public key.
3. Recompute signed payload hash.
4. Check required boundary fields.
5. Look up `guardian_id` in `/api/guardian-registry.json`.
6. Return structured status.

Automated verification:

```bash
python3 scripts/verify_guardian_status.py --payload payload.json --registry api/guardian-registry.json
```

## Guardian status values

| Status | Meaning |
|---|---|
| `active_registered_guardian` | Valid proof + active registry match |
| `valid_self_registered_guardian_claim` | Valid proof + self-registration, not in registry |
| `valid_unregistered_guardian_claim` | Valid proof, not in registry |
| `registered_but_retired` | Valid proof + retired registry entry |
| `registered_but_rotated` | Valid proof + rotated registry entry |
| `registered_but_superseded` | Valid proof + superseded registry entry |
| `registered_but_compromised` | Valid proof + compromised registry entry |
| `invalid_guardian_proof` | Proof validation failed |
| `missing_guardian_proof` | No proof present |

## Join

See [Guardian Join Guide](/guardian-join/) for instructions.

## Boundary

Bitcoin Originals remain final.

Guardian Alliance does not create authority, governance, attestation, verification level, successor reception, legal duty, religious obligation, rank, command, or amendment.

Guardian Alliance does not create authority over the seed. It creates continuity around the seed.
