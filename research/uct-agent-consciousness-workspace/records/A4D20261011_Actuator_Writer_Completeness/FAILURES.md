# A4D failures and retained negative results

1. **No physical installation.** The planned robot-level route test could not be truthfully claimed from the available repository and public sources. The result is a protocol plus exact finite obstruction.
2. **Replay-only criterion failed.** A hidden actuator writer can reproduce every transition and endpoint, so A4C-style action replay does not establish writer identity.
3. **Single challenge failed.** Testing only `q=1` leaves one exact mode-only hidden-writer twin.
4. **Randomness-alone shortcut failed.** If the hidden writer obtains the challenge before actuation, paired/random challenge variation no longer excludes it.
5. **Software inventory shortcut rejected.** Static source/log inspection cannot certify omitted firmware, bus, power, mechanical or human writer paths.
6. **First whole-map validator was too strict.** It treated missing per-rule AND annotations and non-node context endpoints as semantic failures. The corrected audit applies the global `all_of=AND` policy to all 424 rules and records the 81/22 schema variations as retained audit debt.

These failures are preserved as limits, not converted into evidence of no route, no familiarity or no experience.

