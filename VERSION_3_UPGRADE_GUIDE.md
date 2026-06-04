# IT Asset Pipeline System - Version 3

## New Features Designed
1. Modern Analytics Dashboard
2. Dark Mode Support
3. Asset Warranty Tracking
4. Asset Assignment History
5. PDF Report Export
6. Search, Sorting & Pagination
7. Role Based Access Control (Admin/User)
8. Email Notifications
9. Docker Deployment Support
10. Render / Railway Deployment Ready

## Suggested Database Changes
- warranty_expiry
- assigned_to
- assigned_date
- asset_history
- user_role

## Deployment
docker build -t it-asset-system .
docker run -p 5000:5000 it-asset-system
