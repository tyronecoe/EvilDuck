# Composed v2 compatibility update

| Capability | Status / evidence boundary |
|---|---|
| Fourteen suffixed terminated inline aliases | New bounded subset, compiler-function-backed simple forms; software and physical results recorded separately |
| Nonterminated inline aliases | Preserved EvilDuck extension, except raw delimiter tokens now have precedence and ambiguous uses reject |
| Ordinary STRING/STRINGLN | Literal behavior preserved, including closing-token text |
| Multiline blocks and DEFINE | Preserved; delimiter syntax resolved before operand expansion |
| BOM source admission | Reviewed v1 contract unchanged; no Unicode/layout expansion |
| REPEAT, ownership, STOP/restart, quarantine | Preserved bounded integration; relevant composed regression coverage required |
| INJECT_VAR | Still blocked; no renewed investigation |

This candidate is not physically accepted. Same-line handling outside the verified simple subset follows explicit EvilDuck delimiter policy, not a full official runtime claim. V1 sources, package and reports remain unchanged. Exact accepted restart rollback remains mandatory; v1 source/text is not the rollback target. See design/reference/results and acceptance documents.
