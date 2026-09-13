# CPT Reference: WZC Sint-Antonius

**Created:** 2026-09-13  
**Updated:** 2026-09-13 (Multilingual support added)

---

## Overview

3 Custom Post Types with associated taxonomies and meta fields.
**Multilingual support:** Dutch (nl) and English (en) via Polylang.

---

## Language Setup

### Backend Languages
| Language | Code | Status |
|----------|------|--------|
| Dutch | `nl` | Default (source) |
| English | `en` | Secondary |

### Recommended Plugin
**Polylang** (free) - preferred for this project
- Lightweight, well-maintained
- Good translation workflow
- Free version sufficient for 2 languages
- Alternative: WPML (paid, more features)

---

## 1. ACTIVITEITEN (`activiteiten`)

**Purpose:** Blog-style activities feed with photos (Facebook-like)

### Structure
```
activiteiten/
├── Archive: /activiteiten/ (Dutch) | /activities/ (English)
└── Single:  /activiteiten/{slug}/ (Dutch) | /activities/{slug-en}/ (English)
```

### Default Categories (Translated)
| Dutch | English |
|-------|---------|
| Excursies | Excursions |
| Therapie | Therapy |
| Feestdagen | Holidays |
| Sport | Sport |
| Creatief | Creative |
| Maaltijden | Meals |
| Gesprekken | Conversations |

### Meta Fields
| Field Key | Type | Example |
|-----------|------|---------|
| `_activiteit_date` | date | 2026-10-15 |
| `_activiteit_gallery` | textarea (IDs) | 123,456,789 |

### Admin Columns
- Titel
- Datum
- Auteur
- Categorie

### Usage in Frontend
```php
// Query recent activities
$activities = new WP_Query([
    'post_type' => 'activiteiten',
    'posts_per_page' => 6,
    'post_status' => 'publish',
    'meta_key' => '_activiteit_date',
    'orderby' => 'meta_value',
    'order' => 'DESC'
]);

// Get activity date
$date = get_post_meta( $post->ID, '_activiteit_date', true );

// Get gallery IDs
$gallery_ids = get_post_meta( $post->ID, '_activiteit_gallery', true );
$gallery_ids = array_filter( array_map( 'intval', explode( ',', $gallery_ids ) ) );
```

---

## 2. VACATURES (`vacatures`)

**Purpose:** Job listings with application integration

### Structure
```
vacatures/
├── Archive: /vacatures/ (Dutch) | /jobs/ (English)
└── Single:  /vacatures/{slug}/ (Dutch) | /jobs/{slug-en}/ (English)
```

### Default Categories (Translated)
| Dutch | English |
|-------|---------|
| Verpleging | Nursing |
| Zorg | Care |
| Administratie | Administration |
| FDF | Management |
| Theraple | Therapy |

### Meta Fields
| Field Key | Type | Example |
|-----------|------|---------|
| `_vacature_location` | text | Sint-Pieters-Leeuw |
| `_vacature_contract_type` | select | voltijds, deeltijds, dagdienst, nachtdienst |
| `_vacature_start_date` | date | 2026-11-01 |
| `_vacature_application_email` | email | info@stantonius.be |
| `_vacature_status` | select | open, closed, archived |
| `_vacature_featured` | boolean | 1 |

### Contract Types (Translated)
| Dutch | English |
|-------|---------|
| Voltijds | Full-time |
| Deeltijds | Part-time |
| Dagdienst | Day shift |
| Nachtdienst | Night shift |

### Admin Columns
- Titel
- Locatie
- Contract
- Status
- Auteur

### Usage in Frontend
```php
// Query open vacancies
$vacancies = new WP_Query([
    'post_type' => 'vacatures',
    'posts_per_page' => -1,
    'post_status' => 'publish',
    'meta_query' => [
        [
            'key' => '_vacature_status',
            'value' => 'open',
        ]
    ],
    'orderby' => 'meta_value',
    'meta_key' => '_vacature_start_date'
]);

// Get contract type
$contract = get_post_meta( $post->ID, '_vacature_contract_type', true );

// Check if featured
$is_featured = get_post_meta( $post->ID, '_vacature_featured', true ) === '1';
```

---

## 3. TESTIMONIALS (`testimonials`)

**Purpose:** Quotes from residents and family members

### Structure
```
testimonials/ — Not publicly accessible (public => false)
```

### Default Categories (Translated)
| Dutch | English |
|-------|---------|
| Bewoner | Resident |
| Familie | Family |
| Medewerker | Staff |

### Meta Fields
| Field Key | Type | Example |
|-----------|------|---------|
| `_testimonial_author_name` | text | Maria Jansen |
| `_testimonial_author_role` | text | Bewoner / Familie |
| `_testimonial_featured` | boolean | 1 |

### Usage in Frontend
```php
// Query featured testimonials for homepage
$testimonials = new WP_Query([
    'post_type' => 'testimonials',
    'posts_per_page' => 3,
    'post_status' => 'publish',
    'meta_query' => [
        [
            'key' => '_testimonial_featured',
            'value' => '1',
        ]
    ],
    'orderby' => 'menu_order',
    'order' => 'ASC'
]);

// Get author info
$author_name = get_post_meta( $post->ID, '_testimonial_author_name', true );
$author_role = get_post_meta( $post->ID, '_testimonial_author_role', true );
```

---

## File Locations

| File | Path |
|------|------|
| CPT Registration | `wp-content/themes/stantonius/inc/custom-post-types.php` |
| Polylang Integration | `wp-content/themes/stantonius/inc/polylang-integration.php` |
| Theme Functions | `wp-content/themes/stantonius/functions.php` |
| Templates | `wp-content/themes/stantonius/templates/` |

---

## Polylang Setup

### Step 1: Install Polylang
1. Install Polylang plugin (free)
2. Activate on WordPress dashboard
3. Go to Settings → Languages

### Step 2: Configure Languages
1. Add language: English (en)
2. Set Dutch as default language
3. Configure URL structure (e.g., `/en/` for English)

### Step 3: Add CPTs to Languages
1. Go to Settings → Languages
2. Under "Post types", enable translation for:
   - Activiteiten
   - Vacatures
   - Testimonials
3. Under "Taxonomies", enable translation for:
   - Activiteit Categorieën
   - Vacature Categorieën
   - Testimonial Categorieën

### Step 4: Translate Content
1. Create content in Dutch (default)
2. Use the translation editor to add English versions
3. Assign translations to correct language flag

---

## Activation

To activate the CPTs:

1. Copy files to your theme's `inc/` directory
2. Include in `functions.php`:
   ```php
   require get_template_directory() . '/inc/custom-post-types.php';
   require get_template_directory() . '/inc/polylang-integration.php';
   ```
3. Flush rewrite rules (Settings → Permalinks → Save)
4. Verify CPTs appear in WordPress admin
5. Install and configure Polylang for translation

---

## Next Steps

Once CPTs are registered:
- Create template files (`single-activiteiten.php`, `single-vacatures.php`, etc.)
- Build archive pages
- Integrate with ACF fields (optional enhancement)
- Add to navigation menu
- Test translation workflow with Polylang
