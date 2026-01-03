# Settings & Preferences Guide

## Access
- Navigate to **Settings** from the top nav, user dropdown, or mobile menu.
- URL: `/settings/` (authenticated users).

## Theme
- Options: **Dark**, **Light**, **Auto**.
- Changes apply immediately and persist via local storage and a server-side preference.

## Email & Alerts
- **Email notifications**: general account and finance updates.
- **Transaction alerts**: status changes/approvals for your submissions.
- **Weekly digest**: summary of spending and budgets.
- **Product updates**: low-volume product news (optional).

## Persistence
- Preferences are stored per-user (`UserPreference`) and synced to the UI on load.
- Theme preference is also set in a cookie and local storage for quick bootstrap.

## Tips
- Use **Auto** if you want the app to follow the system theme.
- Ensure emails are configured for outbound delivery in production settings.
