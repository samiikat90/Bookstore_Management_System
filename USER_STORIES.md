# User Stories - Chapter 6: A Plot Twist Bookstore

## User Story Template

```
[Story ID] - Story Title
As a [user type]
I want [functionality]
So that [business value/benefit]

Acceptance Criteria:
- [Specific, testable criteria]
- [Additional criteria]

Definition of Done: [Clear completion criteria]
Story Points: [Estimation]
Priority: [High/Medium/Low]
Epic: [Epic name]
Dependencies: [Other stories this depends on]
```

---

## Epic 1: Core E-commerce Platform (Foundation)

### [BSM-001] Application Foundation Setup
**As a** development team 
**I want** a properly structured Flask application 
**So that** we can build features on a reliable foundation 

**Acceptance Criteria:**
- Flask application starts without errors
- Database connection established and tested
- Basic routing responds correctly
- Template rendering functional
- Static file serving works
- Configuration management in place
- Error handling framework implemented

**Definition of Done:** Application runs locally, all basic systems functional 
**Story Points:** 8 
**Priority:** High 
**Epic:** Core E-commerce Platform 
**Dependencies:** None 

---

### [BSM-002] Database Schema Design
**As a** developer 
**I want** a well-designed database schema 
**So that** data is stored efficiently and relationships are clear 

**Acceptance Criteria:**
- User table with authentication fields
- Book table with inventory tracking
- Purchase table for order management
- Customer table for user accounts
- Proper foreign key relationships
- Database migration scripts
- Data validation at model level

**Definition of Done:** All tables created, relationships working, validation in place 
**Story Points:** 13 
**Priority:** High 
**Epic:** Core E-commerce Platform 
**Dependencies:** [BSM-001] 

---

### [BSM-003] Admin Authentication System
**As an** admin user 
**I want** to securely log into the admin dashboard 
**So that** I can manage the bookstore safely 

**Acceptance Criteria:**
- Login form with username/password
- Password hashing with salt
- Session management
- Login required decorators
- Manager role checking
- Logout functionality
- Password validation

**Definition of Done:** Admin login works securely, role-based access enforced 
**Story Points:** 8 
**Priority:** High 
**Epic:** Core E-commerce Platform 
**Dependencies:** [BSM-002] 

---

### [BSM-004] Book Catalog Display
**As a** customer 
**I want** to browse available books with complete information 
**So that** I can find and select books to purchase 

**Acceptance Criteria:**
- Display books with title, author, price, genre
- Show book availability status
- Responsive grid layout for mobile/desktop
- Placeholder for book images
- Clean, professional styling
- Loading states for slow connections

**Definition of Done:** Books display attractively, responsive design works 
**Story Points:** 5 
**Priority:** High 
**Epic:** Core E-commerce Platform 
**Dependencies:** [BSM-002] 

---

### [BSM-005] Basic Order Creation
**As an** admin user 
**I want** to create orders for customers 
**So that** I can process purchases manually 

**Acceptance Criteria:**
- Form to create new purchases
- Customer information collection
- Book selection from catalog
- Quantity specification
- Order total calculation
- Order confirmation display

**Definition of Done:** Orders can be created and saved to database 
**Story Points:** 8 
**Priority:** High 
**Epic:** Core E-commerce Platform 
**Dependencies:** [BSM-002, BSM-004] 

---

## Epic 2: Security & Authentication (Trust)

### [BSM-020] Two-Factor Authentication
**As a** system administrator 
**I want** two-factor authentication for all admin accounts 
**So that** unauthorized access is prevented even with compromised passwords 

**Acceptance Criteria:**
- Email-based 2FA code generation
- 6-digit numeric codes
- 10-minute code expiration
- Secure code storage and validation
- User-friendly setup process
- Backup authentication methods
- Rate limiting for code attempts

**Definition of Done:** 2FA required for all admin logins, secure and reliable 
**Story Points:** 13 
**Priority:** High 
**Epic:** Security & Authentication 
**Dependencies:** [BSM-003] 

---

### [BSM-021] Email Integration System
**As a** system 
**I want** reliable email sending capabilities 
**So that** 2FA codes and notifications can be delivered 

**Acceptance Criteria:**
- SMTP configuration with Gmail
- Email template system
- HTML and plain text support
- Delivery confirmation
- Error handling for failed sends
- Environment variable configuration
- Queue system for bulk emails

**Definition of Done:** Emails send reliably, templates look professional 
**Story Points:** 8 
**Priority:** High 
**Epic:** Security & Authentication 
**Dependencies:** [BSM-020] 

---

### [BSM-022] Session Timeout Management
**As a** security administrator 
**I want** configurable session timeouts 
**So that** inactive sessions don't pose security risks 

**Acceptance Criteria:**
- Configurable timeout duration
- Warning before timeout
- Automatic session extension on activity
- Secure session cleanup
- Grace period for active users
- Dashboard timeout indicators

**Definition of Done:** Sessions timeout appropriately, users warned in advance 
**Story Points:** 5 
**Priority:** Medium 
**Epic:** Security & Authentication 
**Dependencies:** [BSM-003] 

---

### [BSM-023] Auto-logout on Browser Close
**As a** security administrator 
**I want** sessions to end when browsers close 
**So that** shared computers don't retain logged-in sessions 

**Acceptance Criteria:**
- Detect browser close events
- End session automatically
- Don't logout during normal navigation
- Work across different browsers
- Handle browser crashes gracefully
- Configurable per environment

**Definition of Done:** Sessions end on browser close, navigation unaffected 
**Story Points:** 8 
**Priority:** Medium 
**Epic:** Security & Authentication 
**Dependencies:** [BSM-022] 

---

### [BSM-024] Enhanced Password Security
**As a** security administrator 
**I want** strong password requirements and secure handling 
**So that** user accounts are protected from common attacks 

**Acceptance Criteria:**
- Minimum password length enforcement
- Password complexity requirements
- Secure password hashing (bcrypt/Werkzeug)
- Password visibility toggle
- Password strength indicator
- Password change functionality
- Protection against common passwords

**Definition of Done:** Passwords secure, requirements clear to users 
**Story Points:** 5 
**Priority:** Medium 
**Epic:** Security & Authentication 
**Dependencies:** [BSM-003] 

---

## Epic 3: Inventory Management (Control)

### [BSM-030] Complete Book Management
**As an** admin user 
**I want** to add, edit, and delete books in the inventory 
**So that** I can maintain an accurate and current catalog 

**Acceptance Criteria:**
- Add new books with all required fields
- Edit existing book information
- Delete books with confirmation
- ISBN validation and uniqueness
- Required field validation
- Success and error feedback
- Undo capability for accidental deletions

**Definition of Done:** Full CRUD operations work reliably with validation 
**Story Points:** 13 
**Priority:** High 
**Epic:** Inventory Management 
**Dependencies:** [BSM-002] 

---

### [BSM-031] Quantity-Based Book Deletion
**As an** admin user 
**I want** to delete specific quantities of books 
**So that** I can manage partial stock removal without losing the book entirely 

**Acceptance Criteria:**
- Option to delete partial quantities
- Option to delete entire book record
- Safety confirmation dialogs
- Check for pending orders before deletion
- Inventory accuracy after deletion
- Audit trail for quantity changes

**Definition of Done:** Partial and full deletion work with safety checks 
**Story Points:** 8 
**Priority:** Medium 
**Epic:** Inventory Management 
**Dependencies:** [BSM-030] 

---

### [BSM-032] CSV Import/Export System
**As an** admin user 
**I want** to import and export inventory via CSV files 
**So that** I can efficiently manage large inventories and integrate with external systems 

**Acceptance Criteria:**
- Import books from properly formatted CSV
- Export current inventory to CSV
- Handle scientific notation in ISBNs
- Validate CSV format and data
- Error reporting with line numbers
- Preview before import
- Backup before bulk changes

**Definition of Done:** CSV operations work reliably, handle edge cases gracefully 
**Story Points:** 13 
**Priority:** High 
**Epic:** Inventory Management 
**Dependencies:** [BSM-030] 

---

### [BSM-033] Bulk Inventory Operations
**As an** admin user 
**I want** to perform bulk operations on inventory 
**So that** I can efficiently manage large catalogs 

**Acceptance Criteria:**
- Bulk price updates
- Bulk status changes (in-stock/out-of-stock)
- Bulk genre assignments
- Bulk deletion with confirmation
- Progress indicators for long operations
- Rollback capability
- Operation logging

**Definition of Done:** Bulk operations work efficiently with proper feedback 
**Story Points:** 8 
**Priority:** Medium 
**Epic:** Inventory Management 
**Dependencies:** [BSM-032] 

---

### [BSM-034] Genre Classification System
**As an** admin user 
**I want** to assign and manage genres for books 
**So that** customers can easily find books by category 

**Acceptance Criteria:**
- 20+ predefined genre categories
- Genre assignment in add/edit forms
- Genre validation against approved list
- Genre-based filtering for customers
- Genre statistics in admin dashboard
- Ability to add new genres
- Genre migration tools

**Definition of Done:** Genres work throughout system, customers can filter effectively 
**Story Points:** 8 
**Priority:** High 
**Epic:** Inventory Management 
**Dependencies:** [BSM-030] 

---

## Epic 4: Customer Experience (Engagement)

### [BSM-040] Customer Registration System
**As a** potential customer 
**I want** to create an account with the bookstore 
**So that** I can track my orders and save my information 

**Acceptance Criteria:**
- Registration form with email validation
- Username uniqueness checking
- Password confirmation validation
- Optional fields for phone/address
- Email format validation
- Terms of service acceptance
- Welcome email after registration

**Definition of Done:** Registration works smoothly, validation prevents errors 
**Story Points:** 8 
**Priority:** High 
**Epic:** Customer Experience 
**Dependencies:** [BSM-002] 

---

### [BSM-041] Customer Login/Logout System
**As a** registered customer 
**I want** to log into my account 
**So that** I can access my order history and account features 

**Acceptance Criteria:**
- Login with username or email
- Remember me functionality
- Secure session handling
- Password reset option
- Clear logout process
- Login state persistence
- Redirect to intended page after login

**Definition of Done:** Login system works reliably, secure session management 
**Story Points:** 8 
**Priority:** High 
**Epic:** Customer Experience 
**Dependencies:** [BSM-040] 

---

### [BSM-042] Customer Account Dashboard
**As a** logged-in customer 
**I want** a dashboard showing my account information 
**So that** I can see my activity and manage my profile 

**Acceptance Criteria:**
- Display personal information clearly
- Show account creation date
- Display order statistics
- Quick links to key functions
- Professional, clean design
- Mobile-responsive layout
- Easy navigation to other account features

**Definition of Done:** Dashboard informative and easy to use 
**Story Points:** 5 
**Priority:** Medium 
**Epic:** Customer Experience 
**Dependencies:** [BSM-041] 

---

### [BSM-043] Order History Tracking
**As a** customer 
**I want** to view my complete order history 
**So that** I can track my purchases and reorder favorite books 

**Acceptance Criteria:**
- List all past orders chronologically
- Show detailed order information
- Display book titles, authors, prices
- Group orders by purchase date
- Calculate total amounts spent
- Link to individual order details
- Search/filter order history

**Definition of Done:** Order history complete and accurate, easy to navigate 
**Story Points:** 8 
**Priority:** High 
**Epic:** Customer Experience 
**Dependencies:** [BSM-042] 

---

### [BSM-044] Guest Checkout System
**As a** non-registered customer 
**I want** to purchase books without creating an account 
**So that** I can make quick purchases without commitment 

**Acceptance Criteria:**
- Checkout form without registration requirement
- Collect minimum necessary information
- Support all payment methods
- Create order record for tracking
- Send confirmation email
- Option to create account after purchase

**Definition of Done:** Guest checkout works completely, orders tracked properly 
**Story Points:** 13 
**Priority:** High 
**Epic:** Customer Experience 
**Dependencies:** [BSM-004] 

---

### [BSM-052] Advanced Shopping Cart
**As a** customer 
**I want** a sophisticated shopping cart 
**So that** I can efficiently manage my order before checkout 

**Acceptance Criteria:**
- Add/remove items easily
- Update quantities with validation
- Calculate totals automatically
- Apply discount codes
- Persist cart across sessions
- Show item availability
- Clear cart functionality

**Definition of Done:** Cart works flawlessly, calculations always accurate 
**Story Points:** 13 
**Priority:** High 
**Epic:** Customer Experience 
**Dependencies:** [BSM-004] 

---

## Epic 5: Order Processing (Fulfillment)

### [BSM-050] Payment Validation System
**As a** system 
**I want** to validate all payment information 
**So that** fraudulent or invalid transactions are prevented 

**Acceptance Criteria:**
- Luhn algorithm for credit card validation
- Card type detection (Visa, Mastercard, etc.)
- PayPal email format validation
- Bank account number validation
- Expiry date validation
- CVV format checking
- Error messages for invalid data

**Definition of Done:** Payment validation catches all common errors 
**Story Points:** 13 
**Priority:** High 
**Epic:** Order Processing 
**Dependencies:** [BSM-044] 

---

### [BSM-051] Email Notification System
**As an** admin user 
**I want** email notifications for all new orders 
**So that** I can process orders quickly and efficiently 

**Acceptance Criteria:**
- Notifications sent to all admin users
- Include complete order details
- Professional email templates
- Customer confirmation emails
- Order status update notifications
- Configurable notification preferences
- Reliable delivery tracking

**Definition of Done:** All notifications sent reliably, content comprehensive 
**Story Points:** 8 
**Priority:** High 
**Epic:** Order Processing 
**Dependencies:** [BSM-021, BSM-044] 

---

### [BSM-053] Discount Code System
**As a** customer 
**I want** to apply discount codes to my order 
**So that** I can take advantage of promotions and savings 

**Acceptance Criteria:**
- Apply discount codes at checkout
- Validate code existence and rules
- Calculate discounts correctly
- Show original and discounted prices
- Prevent expired code usage
- Limit usage per customer
- Admin interface for code management

**Definition of Done:** Discount system works accurately, prevents abuse 
**Story Points:** 8 
**Priority:** Medium 
**Epic:** Order Processing 
**Dependencies:** [BSM-052] 

---

### [BSM-054] Professional UI Enhancement
**As a** user (customer or admin) 
**I want** a polished, professional interface 
**So that** I have confidence in the system and enjoy using it 

**Acceptance Criteria:**
- Consistent Bootstrap styling
- Professional color scheme
- Font Awesome icons throughout
- Responsive design for all devices
- Loading states and animations
- Clear navigation patterns
- Accessibility compliance

**Definition of Done:** UI looks professional, works on all devices 
**Story Points:** 8 
**Priority:** Medium 
**Epic:** Order Processing 
**Dependencies:** All UI-related stories 

---

## Epic 6: Data Management (Intelligence)

### [BSM-060] Comprehensive Genre Display
**As a** customer 
**I want** to see book genres clearly everywhere 
**So that** I can quickly identify book types and make better choices 

**Acceptance Criteria:**
- Genre badges on all book displays
- Consistent styling across all templates
- Genre information in shopping cart
- Genre shown in order confirmations
- Genre filtering in browse view
- Genre information in emails
- Genre statistics for admin

**Definition of Done:** Genres visible everywhere, styling consistent 
**Story Points:** 8 
**Priority:** Medium 
**Epic:** Data Management 
**Dependencies:** [BSM-034] 

---

### [BSM-061] Genre Management in Admin Forms
**As an** admin user 
**I want** genre dropdown fields in book management 
**So that** I can easily assign and update book genres 

**Acceptance Criteria:**
- Genre dropdown in add book form
- Genre dropdown in edit book form
- Current genre pre-selected in edit
- Validation against approved genre list
- Visual feedback for selections
- Ability to clear genre selection

**Definition of Done:** Genre assignment works smoothly in all admin forms 
**Story Points:** 3 
**Priority:** Medium 
**Epic:** Data Management 
**Dependencies:** [BSM-034, BSM-030] 

---

### [BSM-062] Guest Checkout Email Confirmations
**As a** guest customer 
**I want** detailed email confirmation of my order 
**So that** I have proof of purchase and order tracking information 

**Acceptance Criteria:**
- Email sent immediately after successful order
- Include all order details and items purchased
- Show customer information for verification
- Provide order tracking number
- Include expected processing time
- Professional email template
- Include customer service contact info

**Definition of Done:** Confirmation emails sent reliably with complete information 
**Story Points:** 5 
**Priority:** High 
**Epic:** Data Management 
**Dependencies:** [BSM-044, BSM-051] 

---

### [BSM-063] Admin Order Notification Enhancement
**As an** admin user 
**I want** comprehensive notifications for new guest orders 
**So that** I can process all orders promptly regardless of order type 

**Acceptance Criteria:**
- Email sent to all admin users for guest orders
- Include complete customer details
- Show order contents with book information
- Indicate payment method used
- Include order priority or urgency
- Link to admin dashboard for processing
- Timestamp for order processing SLA

**Definition of Done:** Admin notifications provide all needed information 
**Story Points:** 5 
**Priority:** High 
**Epic:** Data Management 
**Dependencies:** [BSM-062, BSM-051] 

---

### [BSM-064] Enhanced Purchase Confirmation Pages
**As a** customer (guest or registered) 
**I want** detailed confirmation pages after purchase 
**So that** I can verify my order details and know what to expect next 

**Acceptance Criteria:**
- Show complete order summary
- Display customer information
- Include book details with genres
- Show payment method confirmation
- Provide order tracking information
- Include next steps and timeline
- Links to customer service

**Definition of Done:** Confirmation pages informative and reassuring 
**Story Points:** 5 
**Priority:** Medium 
**Epic:** Data Management 
**Dependencies:** [BSM-062] 

---

## Future Backlog Items

### [BSM-070] Mobile Application Development
**As a** mobile user 
**I want** a native mobile app for the bookstore 
**So that** I can shop conveniently from my smartphone 

**Story Points:** 40 
**Priority:** High 
**Epic:** Customer Experience 

---

### [BSM-071] Advanced Analytics Dashboard
**As an** admin user 
**I want** detailed analytics and business intelligence 
**So that** I can make data-driven decisions about inventory and sales 

**Story Points:** 25 
**Priority:** High 
**Epic:** Data Management 

---

### [BSM-072] AI Book Recommendation Engine
**As a** customer 
**I want** personalized book recommendations 
**So that** I can discover books I'm likely to enjoy 

**Story Points:** 30 
**Priority:** High 
**Epic:** Customer Experience 

---

### [BSM-073] Wishlist Functionality
**As a** customer 
**I want** to save books for later purchase 
**So that** I can track books I'm interested in buying 

**Story Points:** 15 
**Priority:** Medium 
**Epic:** Customer Experience 

---

### [BSM-074] Book Reviews and Rating System
**As a** customer 
**I want** to read and write reviews for books 
**So that** I can make informed purchasing decisions 

**Story Points:** 20 
**Priority:** Medium 
**Epic:** Customer Experience 

---

### [BSM-075] Automated Inventory Alerts
**As an** admin user 
**I want** automatic alerts for low stock levels 
**So that** I can reorder books before running out 

**Story Points:** 12 
**Priority:** Medium 
**Epic:** Inventory Management 

---

### [BSM-076] Social Media Integration
**As a** customer 
**I want** to share my book purchases on social media 
**So that** I can recommend books to friends 

**Story Points:** 18 
**Priority:** Medium 
**Epic:** Customer Experience 

---

### [BSM-077] Advanced Search and Filtering
**As a** customer 
**I want** sophisticated search options 
**So that** I can find exactly the books I'm looking for 

**Story Points:** 15 
**Priority:** Medium 
**Epic:** Customer Experience 

---

### [BSM-078] Multi-language Support
**As an** international customer 
**I want** the website in my preferred language 
**So that** I can shop comfortably 

**Story Points:** 35 
**Priority:** Low 
**Epic:** Customer Experience 

---

### [BSM-079] Subscription Service
**As a** book lover 
**I want** monthly book subscription boxes 
**So that** I can discover new books regularly 

**Story Points:** 45 
**Priority:** Low 
**Epic:** Core E-commerce Platform 

---

### [BSM-080] REST API Development
**As a** developer 
**I want** REST API access to bookstore data 
**So that** I can integrate with other systems 

**Story Points:** 30 
**Priority:** Low 
**Epic:** Data Management 

---

## Story Estimation Guide

### **Story Point Scale:**
- **1 Point:** Trivial change, 1-2 hours
- **3 Points:** Simple feature, half day
- **5 Points:** Standard feature, 1 day
- **8 Points:** Complex feature, 2-3 days
- **13 Points:** Very complex feature, 1 week
- **20 Points:** Epic-level, should be broken down
- **40+ Points:** Large epic, multiple sprints

### **Estimation Factors:**
- **Complexity:** How difficult is the technical implementation?
- **Uncertainty:** How well do we understand the requirements?
- **Dependencies:** What other work must be completed first?
- **Testing:** How complex is the testing and validation?
- **Integration:** How many other systems does this touch?

---

**Document Version:** 1.0 
**Last Updated:** November 5, 2025 
**Total Stories:** 45 
**Completed Stories:** 25 
**Remaining Backlog:** 20 stories