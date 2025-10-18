#!/bin/bash

# Pavitra Enterprises - Template Reorganization Script
# Run this from your templates directory

echo "🏗️  Reorganizing template structure..."

# Create new directories
mkdir -p account checkout static_pages

echo "✅ Created directories: account/, checkout/, static_pages/"

# Move account-related files
mv account.html account/account.html 2>/dev/null && echo "✅ Moved account.html → account/account.html"
mv profile.html account/profile.html 2>/dev/null && echo "✅ Moved profile.html → account/profile.html"

# Move checkout-related files  
mv order-confirmation.html checkout/order_confirmation.html 2>/dev/null && echo "✅ Moved order-confirmation.html → checkout/order_confirmation.html"
mv payment-methods.html checkout/payment_methods.html 2>/dev/null && echo "✅ Moved payment-methods.html → checkout/payment_methods.html"
mv checkout.html checkout/checkout.html 2>/dev/null && echo "✅ Moved checkout.html → checkout/checkout.html"

# Move static pages
mv shiping-info.html static_pages/shipping_info.html 2>/dev/null && echo "✅ Moved shiping-info.html → static_pages/shipping_info.html (fixed typo)"
mv about.html static_pages/about.html 2>/dev/null && echo "✅ Moved about.html → static_pages/about.html"
mv contact.html static_pages/contact.html 2>/dev/null && echo "✅ Moved contact.html → static_pages/contact.html"
mv faq.html static_pages/faq.html 2>/dev/null && echo "✅ Moved faq.html → static_pages/faq.html"
mv return-policy.html static_pages/return_policy.html 2>/dev/null && echo "✅ Moved return-policy.html → static_pages/return_policy.html"
mv tos.html static_pages/tos.html 2>/dev/null && echo "✅ Moved tos.html → static_pages/tos.html"
mv privacy.html static_pages/privacy.html 2>/dev/null && echo "✅ Moved privacy.html → static_pages/privacy.html"

# Move search results to shop
mv search-results.html shop/search_results.html 2>/dev/null && echo "✅ Moved search-results.html → shop/search_results.html"

# Remove duplicate files
rm -f category.html 2>/dev/null && echo "✅ Removed duplicate: category.html"
rm -f login.html 2>/dev/null && echo "✅ Removed duplicate: login.html" 
rm -f register.html 2>/dev/null && echo "✅ Removed duplicate: register.html"
rm -f product_details.html 2>/dev/null && echo "✅ Removed duplicate: product_details.html"
rm -f indexbackup.html 2>/dev/null && echo "✅ Removed unused: indexbackup.html"
rm -f starter-page.html 2>/dev/null && echo "✅ Removed unused: starter-page.html"
rm -f support.html 2>/dev/null && echo "✅ Removed unused: support.html"

# Fix any remaining shop files that should be in shop directory
if [ -f "shop/about.html" ]; then
    rm -f static_pages/about.html 2>/dev/null
    echo "✅ Kept shop/about.html (already in correct location)"
fi

if [ -f "shop/contact.html" ]; then
    rm -f static_pages/contact.html 2>/dev/null  
    echo "✅ Kept shop/contact.html (already in correct location)"
fi

echo ""
echo "🎉 Reorganization complete!"
echo ""
echo "📁 New structure:"
echo "   templates/"
echo "   ├── base.html"
echo "   ├── index.html" 
echo "   ├── errors/"
echo "   ├── auth/"
echo "   ├── shop/"
echo "   ├── account/"
echo "   ├── static_pages/"
echo "   ├── admin/"
echo "   └── checkout/"
echo ""
echo "⚠️  Next steps:"
echo "   1. Update your Flask routes to use new paths"
echo "   2. Test all pages to ensure they work"
echo "   3. Commit changes to git"
