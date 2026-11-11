# Entity relationship diagram

The Postgres schema from `supabase/migrations/20261105000000_schema.sql`.
Column details and rules are in `DATABASE_SCHEMA.md`; row-level security, Storage and
Realtime are in `supabase/migrations/20261105000100_rls_storage_realtime.sql`.

Notes:

- Every table except `allergens` and `dish_dietary`/`dish_allergens` (which hang off
  `dishes`) has a `caterer_id`. To keep the diagram readable, only the top-level
  tables draw a line to `caterers`; the rest reach it through their parent, and
  composite foreign keys on `(caterer_id, ...)` keep the whole chain in one caterer.
- Ids are `uuid` (from `gen_random_uuid()`), except `allergens.id`, a `smallint` identity.
- Money columns are `numeric(10, 2)` in the caterer's currency (ILS by default). Quantities are
  `numeric(10, 2)` and portion rules `numeric(5, 2)`. Mermaid can't show the precision,
  so the diagram says `numeric`.
- Times are `timestamptz`; `date` and `time` columns hold a calendar day or a time of day.
- Columns typed with an enum name use Postgres enums; the comment lists the values.
- `caterer_users.auth_user_id` references Supabase's `auth.users`, which is outside this diagram.
- `quantity_rules.caterer_id` is nullable: null is the platform default.

```mermaid
erDiagram
    caterers {
        uuid id PK
        text slug UK
        text name
        text logo_path
        text brand_color
        text contact_phone
        text notification_email
        text kashrut_status
        text kashrut_certificate_path
        kashrut_mixing_rule kashrut_mixing_rule "block | warn"
        char(3) currency
        int ai_monthly_message_limit
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    caterer_users {
        uuid id PK
        uuid caterer_id FK
        uuid auth_user_id UK "Supabase auth.users"
        timestamptz created_at
    }

    customers {
        uuid id PK
        uuid caterer_id FK
        text full_name
        text phone
        text email
        timestamptz created_at
        timestamptz updated_at
    }

    events {
        uuid id PK
        uuid caterer_id FK
        uuid customer_id FK
        text event_type
        date event_date
        int adults
        int children
        int vegetarian_guests
        int vegan_guests
        int restricted_guests
        text dietary_notes
        timestamptz created_at
        timestamptz updated_at
    }

    dish_categories {
        uuid id PK
        uuid caterer_id FK
        text name
        category_type category_type "salad | main | side | dessert | drink | other"
        int sort_order
        boolean is_active
        timestamptz created_at
        timestamptz updated_at
    }

    dishes {
        uuid id PK
        uuid caterer_id FK
        uuid category_id FK
        text name
        text description
        text image_path
        pricing_unit pricing_unit "per_guest | per_tray | per_weight | per_item"
        numeric unit_price
        text unit_label
        numeric servings_per_unit
        int calories_per_portion
        text portion_description
        numeric min_quantity
        boolean is_available
        timestamptz created_at
        timestamptz updated_at
    }

    dish_dietary {
        uuid dish_id PK, FK
        kashrut_class kashrut_class "meat | dairy | pareve, null = unknown"
        boolean is_vegetarian "null = unknown"
        boolean is_vegan "null = unknown"
        timestamptz verified_at
    }

    allergens {
        smallint id PK
        text name UK
    }

    dish_allergens {
        uuid dish_id PK, FK
        smallint allergen_id PK, FK
        allergen_status status "contains | free | unknown, no row = unknown"
    }

    delivery_zones {
        uuid id PK
        uuid caterer_id FK
        text name
        numeric fee
        jsonb definition
        boolean is_active
    }

    time_slots {
        uuid id PK
        uuid caterer_id FK
        fulfillment_type fulfillment_type "pickup | delivery"
        smallint weekday "0-6"
        time start_time
        time end_time
        int capacity
        boolean is_active
    }

    blocked_dates {
        uuid id PK
        uuid caterer_id FK
        date date
        text reason
    }

    quantity_rules {
        uuid id PK
        uuid caterer_id FK "null = platform default"
        category_type category_type
        numeric portions_per_adult
        numeric portions_per_child
    }

    orders {
        uuid id PK
        uuid caterer_id FK
        text access_token_hash UK
        uuid customer_id FK
        uuid event_id FK, UK
        order_status status "draft | pending_approval | approved | rejected"
        int version
        fulfillment_type fulfillment_type
        timestamptz requested_at
        uuid time_slot_id FK
        text delivery_city
        text delivery_address
        uuid delivery_zone_id FK
        numeric subtotal
        numeric delivery_fee
        numeric total
        boolean kashrut_warning_acknowledged
        timestamptz submitted_at
        timestamptz decided_at
        text decision_note
        timestamptz created_at
        timestamptz updated_at
    }

    order_items {
        uuid id PK
        uuid caterer_id FK
        uuid order_id FK
        uuid dish_id FK
        numeric quantity
        text snapshot_name
        pricing_unit snapshot_pricing_unit
        numeric snapshot_unit_price
        numeric snapshot_line_total
    }

    ai_conversations {
        uuid id PK
        uuid caterer_id FK
        uuid order_id FK, UK
        timestamptz created_at
    }

    ai_messages {
        uuid id PK
        uuid caterer_id FK
        uuid conversation_id FK
        text role "user | assistant | tool"
        jsonb content
        timestamptz created_at
    }

    ai_change_proposals {
        uuid id PK
        uuid caterer_id FK
        uuid order_id FK
        uuid conversation_id FK
        int base_order_version
        jsonb changes
        text rationale
        numeric price_before
        numeric price_after
        proposal_status status "pending | approved | rejected | expired | failed"
        timestamptz created_at
        timestamptz decided_at
        timestamptz executed_at
    }

    ai_usage {
        uuid caterer_id PK, FK
        date month PK
        int message_count
    }

    caterers ||--o{ caterer_users : "has logins"
    caterers ||--o{ customers : "has"
    caterers ||--o{ dish_categories : "has menu"
    caterers ||--o{ delivery_zones : "delivers to"
    caterers ||--o{ time_slots : "offers"
    caterers ||--o{ blocked_dates : "closes on"
    caterers |o--o{ quantity_rules : "overrides"
    caterers ||--o{ ai_usage : "uses AI"

    customers ||--o{ events : "plans"
    customers ||--o{ orders : "places"
    events ||--o| orders : "ordered as"

    dish_categories ||--o{ dishes : "contains"
    dishes ||--o| dish_dietary : "dietary info"
    dishes ||--o{ dish_allergens : "allergen status"
    allergens ||--o{ dish_allergens : "listed in"

    orders ||--o{ order_items : "contains"
    dishes ||--o{ order_items : "ordered as"
    delivery_zones |o--o{ orders : "delivery zone"
    time_slots |o--o{ orders : "time slot"

    orders ||--o| ai_conversations : "chat"
    ai_conversations ||--o{ ai_messages : "messages"
    orders ||--o{ ai_change_proposals : "proposals"
    ai_conversations |o--o{ ai_change_proposals : "proposed in"
```
