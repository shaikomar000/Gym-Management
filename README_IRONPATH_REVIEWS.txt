IRONPATH UPDATE - MEMBER REVIEWS + BRANCH LOCATION BUTTON

WHAT CHANGED
- Public GET /api/reviews returns real rows from the MySQL reviews table.
- POST /api/reviews requires a logged-in account and saves the account's own name/id.
- Any verified account can review; an active paid membership is NOT required.
- Review text is validated (1-2000 chars) and rating must be 1-5.
- /reviews now renders its own reviews page; the home page also shows database reviews.
- Branch cards use a Google Maps search link instead of Contact Branch.
- Existing dark-green styling is retained.

INSTALL
1. Back up the gym database and current IronPath project folder.
2. In phpMyAdmin, select database gym > SQL and run migration_reviews.sql once.
   This adds nullable reviews.user_id and an index. Existing reviews are preserved.
3. Copy this ZIP's main.py and formula.py into the project root.
4. Copy templates/* into the project's templates folder (overwrite same-named files).
5. Copy static/js/app.js and static/css/style.css into the matching static folders.
6. Restart Flask and test /reviews while logged out and logged in.

IMPORTANT
- The current branch card addresses in app.js are still the existing sample labels
  Madhapur, Kukatpally and Gachibowli, Hyderabad. Replace these with exact branch
  addresses before publishing so Google Maps opens the correct premises.
- The existing account login flow verifies email before creating an authenticated
  session. Therefore only verified, logged-in accounts can post.
- This update does not alter existing reviews or other database tables.
- Keep SECRET_KEY and database credentials in environment variables for deployment.

Membership system removal: membership plans, membership page links, membership-only workout gating, and admin membership/renewal screens have been removed. Accounts remain required to access private workout features. /membership redirects to /signup for old bookmarks.
