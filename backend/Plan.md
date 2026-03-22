**Implementation Plan**
Great direction. Here is a practical rollout plan from highest impact to lowest risk.

1. Slim redirect cache payload first
- What to change:
  - Create a redirect-focused cache shape in urlHelper.py with only id, original_url, expires_at.
  - Keep the existing broader URL cache for dashboard/profile APIs if needed.
  - Add a separate key helper in cache.py, for example a redirect key namespace.
- Why it improves performance:
  - Smaller Redis payload means faster serialization/deserialization and lower memory usage.
  - Better cache density gives more hot keys in memory and fewer evictions.
- Validation:
  - Compare p50/p95 redirect latency before vs after.
  - Track Redis memory used and key count.

2. Strict cache invalidation on update/delete
- What to change:
  - In update flow in url.py, invalidate both:
    - short_code-based key
    - id-based key (if used by other APIs)
  - In delete flow in url.py, keep deleting all related keys (already partly done, extend to any new redirect key).
- Why it improves correctness:
  - Prevents stale redirects after URL edit.
  - Prevents stale reads from dashboard/detail endpoints.
- Validation:
  - Edit a URL, then hit redirect immediately and confirm new destination.
  - Delete a URL, confirm redirect returns 404 without serving stale cache.

3. Add negative cache for not-found short codes
- What to change:
  - In lookup helper urlHelper.py, when DB returns no URL, set a short-lived negative marker (for example 5-15 seconds).
  - On read, if marker exists, return not found immediately without DB query.
  - Add TTL constant in cache.py.
- Why it improves resilience:
  - Protects DB from repeated random/bruteforce short_code misses.
  - Smooths traffic spikes on invalid requests.
- Validation:
  - Load test invalid short_code traffic and confirm DB query count drops sharply.

4. Prepare async click logging queue (phase 2)
- What to change:
  - Keep current background task now in main.py and click_service.py.
  - Add queue abstraction interface first (producer in redirect path, worker consumer later).
  - Start with Redis list/stream or a broker when traffic justifies.
- Why it improves scalability:
  - Redirect path becomes mostly read-only and independent from click write pressure.
  - Better burst handling and fewer tail-latency spikes.
- Validation:
  - Under high QPS, redirect latency remains stable while click writes are eventually consistent.

**Suggested Rollout Order**
1. Slim payload
2. Strict invalidation
3. Negative cache
4. Async queue

**Expected Outcome**
- Faster redirects due to true cache-hot path and smaller values.
- Better cache correctness after edit/delete.
- Lower DB load during invalid-code scans.
- Clear path to scale analytics logging independently.

**Success Metrics To Track**
1. Redirect p50/p95/p99 latency
2. Cache hit ratio for short_code lookup
3. DB queries per redirect request
4. Not-found request DB query reduction after negative cache
5. Redis memory usage and eviction rate

If you want, I can implement Phase 1 and Phase 2 next in one safe patch set so you get immediate speed + correctness gains.