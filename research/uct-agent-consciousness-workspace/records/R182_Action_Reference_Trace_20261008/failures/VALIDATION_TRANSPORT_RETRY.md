# Validation transport retry

The first combined pre-save validation command was not completed because the execution transport disconnected. This was an infrastructure failure, not a failed model assertion.

The same substantive checks were immediately rerun in a fresh command: 64 configurations, 12/12 assertions, JSON parsing, graph SHA256 and `git diff --check` all completed. The initial interrupted run is recorded so that silence or transport failure is not misreported as theoretical success or failure.
