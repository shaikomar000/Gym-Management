IRONPATH INTEGRATION UPDATE

This package includes:
- main.py: Flask authentication, email OTP, login/logout, password reset, workout/cardio APIs, member attendance requests and admin approval endpoints.
- templates/ and static/: current frontend plus integrated data-loading JavaScript and Chart.js.
- migration.sql: database changes needed to associate workout/cardio rows with accounts and allow pending attendance requests.

BEFORE RUNNING:
1. Back up your gym database.
2. Run migration.sql in phpMyAdmin against the gym database. Run it only once. If a column already exists, remove that ALTER statement before running.
3. Install dependencies: pip install Flask Flask-SQLAlchemy PyMySQL
4. Set environment variables in PowerShell (use your own values):
   $env:SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
   $env:SMTP_HOST="smtp.gmail.com"
   $env:SMTP_PORT="465"
   $env:SMTP_USER="your-gmail@gmail.com"
   $env:SMTP_PASSWORD="your-google-app-password"
   $env:SMTP_FROM="your-gmail@gmail.com"
   $env:IRONPATH_ADMIN_EMAIL="shaikomar000@gmail.com"
5. Ensure templates/index.html and the other existing site templates (branches.html, coaches.html, contact.html) are present. This package includes a simple index placeholder; replace it with your actual home template if you have one.
6. Run: python main.py

ADMIN:
The configured admin email is shaikomar000@gmail.com. Register this email through signup and verify its OTP. Only that verified account can open /admin. To transfer the product later, change IRONPATH_ADMIN_EMAIL; do not rely on a permanent hardcoded owner email.

IMPORTANT DATABASE NOTES:
- Existing workout/cardio rows are retained with user_id NULL; they cannot be attributed to a member retroactively.
- Existing cardio/workout date fields in your dump are DATETIME already; the MODIFY statements standardize expected precision.
- Attendance approved values: 0 pending, 1 approved, 2 rejected.
- The original attendance table has no foreign keys. This update keeps its existing shape and stores admin_id NULL until a decision.
- No payment gateway or membership billing is implemented; payment was intentionally deferred.
- Configure SMTP before testing signup OTP or forgot-password OTP.
- For production, turn debug off, use HTTPS, CSRF protection, login rate limiting, secure cookie settings and a production secret manager.

Membership system removal: membership plans, membership page links, membership-only workout gating, and admin membership/renewal screens have been removed. Accounts remain required to access private workout features. /membership redirects to /signup for old bookmarks.
