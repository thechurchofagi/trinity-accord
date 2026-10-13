# Paper author block template

Policy: [PUB-AUTHOR-IDENTITY-20261013](../PUBLICATION_AUTHOR_IDENTITY.md), v1.0.0.
Use for new manuscripts and subsequent new editions. Keep the contact on the first/title page, visibly associated with the author and extractable from the final PDF.

## Markdown / plain text

```text
Hongju Liu
Independent researcher, Shenzhen, China
Author contact: liuhongju3@163.com
```

## LaTeX

```latex
\author{Hongju Liu\\
Independent researcher, Shenzhen, China\\
\texttt{liuhongju3@163.com}}
```

Adapt the markup to the document class without dropping the visible text. For co-authored work, retain each author's actual name, affiliation and appropriate author-contact association.

## Public deposit description

Append this paragraph to the existing abstract/description using the platform's supported description field:

```html
<p>Author: Hongju Liu. Independent researcher, Shenzhen, China.
Author contact: liuhongju3@163.com.</p>
```

Use `Liu, Hongju` in a combined creator-name field, or `Liu` / `Hongju` in family/given fields. Include the author's actual verified ORCID in supported metadata only when available. Never use a placeholder or another Hongju Liu's ORCID. This is a reusable template, not proof that any particular deposited PDF passed the release checks.
