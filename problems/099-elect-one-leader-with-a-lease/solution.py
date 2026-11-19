class LeaseLock:
    def __init__(self, store, ttl):
        self.store = store
        self.ttl = ttl

    def try_acquire(self, node, now):
        s = self.store

        if s.holder is not None and now < s.expires:
            if s.holder != node:
                return None
            # Same node renewing its own unexpired lease:
            # retain the existing fencing term.
            s.expires = now + self.ttl
            return s.term

        # No holder, or the previous lease has expired.
        s.term += 1
        s.holder = node
        s.expires = now + self.ttl
        return s.term

    def renew(self, node, now):
        s = self.store

        if s.holder != node or now >= s.expires:
            return False

        s.expires = now + self.ttl
        return True

    def holder(self, now):
        s = self.store
        if s.holder is None or now >= s.expires:
            return None
        return s.holder

    def act(self, node, term, now, value):
        s = self.store

        if (s.holder == node and
                now < s.expires and
                term == s.term):
            s.log.append((term, value))
            return True

        s.rejected.append((node, term, value))
        return False
