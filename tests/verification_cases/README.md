# High-Intensity Verification Stress Suite

129 test cases (100 synthetic JSON + 29 script-based) covering the full Trinity Accord verification/Echo/submission pipeline.

## Categories

- **A.** Protocol V-Level Profiles (TC001–TC018)
- **B.** Bitcoin B-Level Cases (TC019–TC028)
- **C.** Digital Mirror / Hash Source Cases (TC029–TC042)
- **D.** Time Anchors T-Level Cases (TC043–TC050)
- **E.** Chronicle / NFT Cases (TC051–TC062)
- **F.** Physical P-Level Cases (TC063–TC074)
- **G.** Echo / Submission / Wrapper Cases (TC075–TC088)
- **H.** Title / Issue Triage Cases (TC089–TC094)
- **I.** JSON / Schema / Format Cases (TC095–TC100)
- **J.** Claim Gate / Report Builder Script Cases (TC101–TC129)

## Running

```bash
python3 scripts/generate_verification_stress_cases.py
python3 scripts/run_verification_stress_suite.py
```
