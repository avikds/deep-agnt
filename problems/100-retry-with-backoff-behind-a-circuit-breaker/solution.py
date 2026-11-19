def call_with_retry(fn, clock, policy, breaker=None):
    for attempt in range(policy["max_attempts"]):
        now = clock.now

        if breaker is not None and not breaker.allow(now):
            raise CircuitOpen()

        try:
            result = fn()
        except (RateLimited, Unavailable) as error:
            if breaker is not None:
                breaker.record_failure(clock.now)

            if attempt + 1 == policy["max_attempts"]:
                raise

            delay = min(
                policy["cap"],
                policy["base"] * (2 ** attempt)
            ) + jitter(attempt)

            retry_after = getattr(error, "retry_after", None)
            if retry_after is not None:
                delay = max(delay, retry_after)

            clock.sleep(delay)

        except Exception:
            raise

        else:
            if breaker is not None:
                breaker.record_success()
            return result


class Breaker:
    def __init__(self, threshold, cooldown):
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.opened_at = None
        self.half_open_trial = False

    def allow(self, now):
        if self.opened_at is None:
            return True

        if now - self.opened_at < self.cooldown:
            return False

        if self.half_open_trial:
            return False

        self.half_open_trial = True
        return True

    def record_success(self):
        self.failures = 0
        self.opened_at = None
        self.half_open_trial = False

    def record_failure(self, now):
        self.failures += 1

        if self.half_open_trial or self.failures >= self.threshold:
            self.opened_at = now
            self.half_open_trial = False
