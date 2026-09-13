<?php
/**
 * Custom Post Types for WZC Sint-Antonius
 *
 * Supports multilingual: Dutch (nl) and English (en)
 * Requires: Polylang or WPML for string translation
 *
 * @package stantonius
 * @version 1.1.0
 */

// Prevent direct access
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Register Custom Post Types with multilingual support
 */
function stantonius_register_cpts() {

    // ============================================
    // 1. ACTIVITEITEN (Activities)
    // ============================================
    register_post_type( 'activiteiten', [
        'labels'              => [
            'name'               => __( 'Activiteiten', 'stantonius' ),
            'singular_name'      => __( 'Activiteit', 'stantonius' ),
            'add_new'            => __( 'Nieuwe activiteit', 'stantonius' ),
            'add_new_item'       => __( 'Nieuwe activiteit toevoegen', 'stantonius' ),
            'edit_item'          => __( 'Activiteit bewerken', 'stantonius' ),
            'new_item'           => __( 'Nieuwe activiteit', 'stantonius' ),
            'view_item'          => __( 'Bekijk activiteit', 'stantonius' ),
            'search_items'       => __( 'Zoek activiteiten', 'stantonius' ),
            'not_found'          => __( 'Geen activiteiten gevonden', 'stantonius' ),
            'not_found_in_trash' => __( 'Geen activiteiten in prullenbak', 'stantonius' ),
            'all_items'          => __( 'Alle activiteiten', 'stantonius' ),
        ],
        'description'         => __( 'Blog-style posts for activity reports with photos', 'stantonius' ),
        'public'              => true,
        'has_archive'         => true,
        'show_in_rest'        => true,
        'menu_icon'           => 'dashicons-calendar-alt',
        'menu_position'       => 5,
        'supports'            => [ 'title', 'editor', 'author', 'thumbnail', 'excerpt', 'custom-fields' ],
        'rewrite'             => [ 'slug' => 'activiteiten', 'with_front' => false ],
        'capability_type'     => 'post',
        'show_in_menu'        => true,
    ] );

    // ============================================
    // 2. VACATURES (Vacancies/Jobs)
    // ============================================
    register_post_type( 'vacatures', [
        'labels'              => [
            'name'               => __( 'Vacatures', 'stantonius' ),
            'singular_name'      => __( 'Vacature', 'stantonius' ),
            'add_new'            => __( 'Nieuwe vacature', 'stantonius' ),
            'add_new_item'       => __( 'Nieuwe vacature toevoegen', 'stantonius' ),
            'edit_item'          => __( 'Vacature bewerken', 'stantonius' ),
            'new_item'           => __( 'Nieuwe vacature', 'stantonius' ),
            'view_item'          => __( 'Bekijk vacature', 'stantonius' ),
            'search_items'       => __( 'Zoek vacatures', 'stantonius' ),
            'not_found'          => __( 'Geen vacatures gevonden', 'stantonius' ),
            'not_found_in_trash' => __( 'Geen vacatures in prullenbak', 'stantonius' ),
            'all_items'          => __( 'Alle vacatures', 'stantonius' ),
        ],
        'description'         => __( 'Job listings with application form integration', 'stantonius' ),
        'public'              => true,
        'has_archive'         => true,
        'show_in_rest'        => true,
        'menu_icon'           => 'dashicons-businessman',
        'menu_position'       => 6,
        'supports'            => [ 'title', 'editor', 'thumbnail', 'custom-fields' ],
        'rewrite'             => [ 'slug' => 'vacatures', 'with_front' => false ],
        'capability_type'     => 'post',
    ] );

    // ============================================
    // 3. TESTIMONIALS
    // ============================================
    register_post_type( 'testimonials', [
        'labels'              => [
            'name'               => __( 'Testimonials', 'stantonius' ),
            'singular_name'      => __( 'Testimonial', 'stantonius' ),
            'add_new'            => __( 'Nieuw testimonial', 'stantonius' ),
            'add_new_item'       => __( 'Nieuw testimonial toevoegen', 'stantonius' ),
            'edit_item'          => __( 'Testimonial bewerken', 'stantonius' ),
            'new_item'           => __( 'Nieuw testimonial', 'stantonius' ),
            'view_item'          => __( 'Bekijk testimonial', 'stantonius' ),
            'search_items'       => __( 'Zoek testimonials', 'stantonius' ),
            'not_found'          => __( 'Geen testimonials gevonden', 'stantonius' ),
            'not_found_in_trash' => __( 'Geen testimonials in prullenbak', 'stantonius' ),
            'all_items'          => __( 'Alle testimonials', 'stantonius' ),
        ],
        'description'         => __( 'Quotes from residents and family members', 'stantonius' ),
        'public'              => false, // Not publicly queryable, admin only
        'show_in_rest'        => true,
        'menu_icon'           => 'dashicons-format-quote',
        'menu_position'       => 6,
        'supports'            => [ 'title', 'editor', 'thumbnail', 'custom-fields' ],
        'rewrite'             => false,
        'capability_type'     => 'post',
        'show_in_menu'        => true,
    ] );
}
add_action( 'init', 'stantonius_register_cpts' );

/**
 * Register Custom Taxonomies with multilingual support
 */
function stantonius_register_taxonomies() {

    // Activiteit Categorieën
    register_taxonomy( 'activiteit_cat', 'activiteiten', [
        'labels'            => [
            'name'              => __( 'Activiteit Categorieën', 'stantonius' ),
            'singular_name'     => __( 'Activiteit Categorie', 'stantonius' ),
            'search_items'      => __( 'Zoek categorieën', 'stantonius' ),
            'all_items'         => __( 'Alle categorieën', 'stantonius' ),
            'edit_item'         => __( 'Categorie bewerken', 'stantonius' ),
            'update_item'       => __( 'Categorie bijwerken', 'stantonius' ),
            'add_new_item'      => __( 'Nieuwe categorie', 'stantonius' ),
            'new_item_name'     => __( 'Nieuw categorie naam', 'stantonius' ),
            'menu_name'         => __( 'Categorieën', 'stantonius' ),
        ],
        'hierarchical'      => true,
        'show_in_rest'      => true,
        'rewrite'           => [ 'slug' => 'activiteit-categorie', 'with_front' => false ],
        'show_admin_column' => true,
    ] );

    // Vacature Categorien
    register_taxonomy( 'vacature_cat', 'vacatures', [
        'labels'            => [
            'name'              => __( 'Vacature Categorieën', 'stantonius' ),
            'singular_name'     => __( 'Vacature Categorie', 'stantonius' ),
            'search_items'      => __( 'Zoek categorieën', 'stantonius' ),
            'all_items'         => __( 'Alle categorieën', 'stantonius' ),
            'edit_item'         => __( 'Categorie bewerken', 'stantonius' ),
            'update_item'       => __( 'Categorie bijwerken', 'stantonius' ),
            'add_new_item'      => __( 'Nieuwe categorie', 'stantonius' ),
            'new_item_name'     => __( 'Nieuw categorie naam', 'stantonius' ),
            'menu_name'         => __( 'Categorieën', 'stantonius' ),
        ],
        'hierarchical'      => true,
        'show_in_rest'      => true,
        'rewrite'           => [ 'slug' => 'vacature-categorie', 'with_front' => false ],
        'show_admin_column' => true,
    ] );

    // Testimonial Categorieën
    register_taxonomy( 'testimonial_cat', 'testimonials', [
        'labels'            => [
            'name'              => __( 'Testimonial Categorieën', 'stantonius' ),
            'singular_name'     => __( 'Testimonial Categorie', 'stantonius' ),
            'search_items'      => __( 'Zoek categorieën', 'stantonius' ),
            'all_items'         => __( 'Alle categorieën', 'stantonius' ),
            'edit_item'         => __( 'Categorie bewerken', 'stantonius' ),
            'update_item'       => __( 'Categorie bijwerken', 'stantonius' ),
            'add_new_item'      => __( 'Nieuwe categorie', 'stantonius' ),
            'new_item_name'     => __( 'Nieuw categorie naam', 'stantonius' ),
            'menu_name'         => __( 'Categorieën', 'stantonius' ),
        ],
        'hierarchical'      => true,
        'show_in_rest'      => true,
        'rewrite'           => false,
        'show_admin_column' => true,
    ] );
}
add_action( 'init', 'stantonius_register_taxonomies' );

/**
 * Add custom meta boxes for CPTs
 */
function stantonius_add_meta_boxes() {

    // Activiteiten meta box
    add_meta_box(
        'activiteit_details',
        __( 'Activiteit Details', 'stantonius' ),
        'stantonius_activiteit_meta_callback',
        'activiteiten',
        'normal',
        'high'
    );

    // Vacatures meta box
    add_meta_box(
        'vacature_details',
        __( 'Vacature Details', 'stantonius' ),
        'stantonius_vacature_meta_callback',
        'vacatures',
        'normal',
        'high'
    );

    // Testimonials meta box
    add_meta_box(
        'testimonial_details',
        __( 'Testimonial Details', 'stantonius' ),
        'stantonius_testimonial_meta_callback',
        'testimonials',
        'normal',
        'high'
    );
}
add_action( 'add_meta_boxes', 'stantonius_add_meta_boxes' );

/**
 * Activiteit Meta Box Callback
 */
function stantonius_activiteit_meta_callback( $post ) {
    wp_nonce_field( 'stantonius_activiteit_meta', 'stantonius_activiteit_nonce' );

    $date = get_post_meta( $post->ID, '_activiteit_date', true );
    $gallery = get_post_meta( $post->ID, '_activiteit_gallery', true );

    ?>
    <table class="form-table">
        <tr>
            <th><label for="activiteit_date"><?php _e( 'Activiteit Datum', 'stantonius' ); ?></label></th>
            <td><input type="date" id="activiteit_date" name="activiteit_date" value="<?php echo esc_attr( $date ); ?>" class="regular-text" /></td>
        </tr>
        <tr>
            <th><label for="activiteit_gallery"><?php _e( 'Gallery IDs (comma separated)', 'stantonius' ); ?></label></th>
            <td><input type="text" id="activiteit_gallery" name="activiteit_gallery" value="<?php echo esc_attr( $gallery ); ?>" class="large-text" placeholder="123,456,789" /></td>
        </tr>
    </table>
    <?php
}

/**
 * Vacature Meta Box Callback
 */
function stantonius_vacature_meta_callback( $post ) {
    wp_nonce_field( 'stantonius_vacature_meta', 'stantonius_vacature_nonce' );

    $location = get_post_meta( $post->ID, '_vacature_location', true );
    $contract_type = get_post_meta( $post->ID, '_vacature_contract_type', true );
    $start_date = get_post_meta( $post->ID, '_vacature_start_date', true );
    $application_email = get_post_meta( $post->ID, '_vacature_application_email', true );
    $status = get_post_meta( $post->ID, '_vacature_status', true );
    $featured = get_post_meta( $post->ID, '_vacature_featured', true );

    ?>
    <table class="form-table">
        <tr>
            <th><label for="vacature_location"><?php _e( 'Locatie', 'stantonius' ); ?></label></th>
            <td><input type="text" id="vacature_location" name="vacature_location" value="<?php echo esc_attr( $location ); ?>" class="regular-text" /></td>
        </tr>
        <tr>
            <th><label for="vacature_contract_type"><?php _e( 'Contracttype', 'stantonius' ); ?></label></th>
            <td>
                <select id="vacature_contract_type" name="vacature_contract_type">
                    <option value="" <?php selected( $contract_type, '' ); ?>>-- Selecteer --</option>
                    <option value="voltijds" <?php selected( $contract_type, 'voltijds' ); ?>>Voltijds</option>
                    <option value="deeltijds" <?php selected( $contract_type, 'deeltijds' ); ?>>Deeltijds</option>
                    <option value="dagdienst" <?php selected( $contract_type, 'dagdienst' ); ?>>Dagdienst</option>
                    <option value="nachtdienst" <?php selected( $contract_type, 'nachtdienst' ); ?>>Nachtdienst</option>
                </select>
            </td>
        </tr>
        <tr>
            <th><label for="vacature_start_date"><?php _e( 'Startdatum', 'stantonius' ); ?></label></th>
            <td><input type="date" id="vacature_start_date" name="vacature_start_date" value="<?php echo esc_attr( $start_date ); ?>" class="regular-text" /></td>
        </tr>
        <tr>
            <th><label for="vacature_application_email"><?php _e( 'Application Email', 'stantonius' ); ?></label></th>
            <td><input type="email" id="vacature_application_email" name="vacature_application_email" value="<?php echo esc_attr( $application_email ); ?>" class="regular-text" /></td>
        </tr>
        <tr>
            <th><label for="vacature_status"><?php _e( 'Status', 'stantonius' ); ?></label></th>
            <td>
                <select id="vacature_status" name="vacature_status">
                    <option value="open" <?php selected( $status, 'open' ); ?>>Open</option>
                    <option value="closed" <?php selected( $status, 'closed' ); ?>>Gesloten</option>
                    <option value="archived" <?php selected( $status, 'archived' ); ?>>Gearchiveerd</option>
                </select>
            </td>
        </tr>
        <tr>
            <th><label for="vacature_featured"><?php _e( 'Featured', 'stantonius' ); ?></label></th>
            <td><input type="checkbox" id="vacature_featured" name="vacature_featured" value="1" <?php checked( $featured, '1' ); ?> /></td>
        </tr>
    </table>
    <?php
}

/**
 * Testimonial Meta Box Callback
 */
function stantonius_testimonial_meta_callback( $post ) {
    wp_nonce_field( 'stantonius_testimonial_meta', 'stantonius_testimonial_nonce' );

    $author_name = get_post_meta( $post->ID, '_testimonial_author_name', true );
    $author_role = get_post_meta( $post->ID, '_testimonial_author_role', true );
    $featured = get_post_meta( $post->ID, '_testimonial_featured', true );

    ?>
    <table class="form-table">
        <tr>
            <th><label for="testimonial_author_name"><?php _e( 'Naam', 'stantonius' ); ?></label></th>
            <td><input type="text" id="testimonial_author_name" name="testimonial_author_name" value="<?php echo esc_attr( $author_name ); ?>" class="regular-text" /></td>
        </tr>
        <tr>
            <th><label for="testimonial_author_role"><?php _e( 'Rol', 'stantonius' ); ?></label></th>
            <td>
                <input type="text" id="testimonial_author_role" name="testimonial_author_role" value="<?php echo esc_attr( $author_role ); ?>" class="regular-text" placeholder="<?php _e( 'Bewoner, Familie, Medewerker', 'stantonius' ); ?>" />
            </td>
        </tr>
        <tr>
            <th><label for="testimonial_featured"><?php _e( 'Featured (show on homepage)', 'stantonius' ); ?></label></th>
            <td><input type="checkbox" id="testimonial_featured" name="testimonial_featured" value="1" <?php checked( $featured, '1' ); ?> /></td>
        </tr>
    </table>
    <?p
}

/**
 * Save Meta Box Data
 */
function stantonius_save_meta_boxes( $post_id ) {

    // Security checks
    if ( ! isset( $_POST['stantonius_activiteit_nonce'] ) || ! wp_verify_nonce( $_POST['stantonius_activiteit_nonce'], 'stantonius_activiteit_meta' ) ) {
        return;
    }
    if ( ! isset( $_POST['stantonius_vacature_nonce'] ) || ! wp_verify_nonce( $_POST['stantonius_vacature_nonce'], 'stantonius_vacature_meta' ) ) {
        return;
    }
    if ( ! isset( $_POST['stantonius_testimonial_nonce'] ) || ! wp_verify_nonce( $_POST['stantonius_testimonial_nonce'], 'stantonius_testimonial_meta' ) ) {
        return;
    }

    // Check permissions
    if ( ! current_user_can( 'edit_post', $post_id ) ) {
        return;
    }

    // Save Activiteit meta
    if ( isset( $_POST['activiteit_date'] ) ) {
        update_post_meta( $post_id, '_activiteit_date', sanitize_text_field( $_POST['activiteit_date'] ) );
    }
    if ( isset( $_POST['activiteit_gallery'] ) ) {
        update_post_meta( $post_id, '_activiteit_gallery', sanitize_textarea_field( $_POST['activiteit_gallery'] ) );
    }

    // Save Vacature meta
    if ( isset( $_POST['vacature_location'] ) ) {
        update_post_meta( $post_id, '_vacature_location', sanitize_text_field( $_POST['vacature_location'] ) );
    }
    if ( isset( $_POST['vacature_contract_type'] ) ) {
        update_post_meta( $post_id, '_vacature_contract_type', sanitize_text_field( $_POST['vacature_contract_type'] ) );
    }
    if ( isset( $_POST['vacature_start_date'] ) ) {
        update_post_meta( $post_id, '_vacature_start_date', sanitize_text_field( $_POST['vacature_start_date'] ) );
    }
    if ( isset( $_POST['vacature_application_email'] ) ) {
        update_post_meta( $post_id, '_vacature_application_email', sanitize_email( $_POST['vacature_application_email'] ) );
    }
    if ( isset( $_POST['vacature_status'] ) ) {
        update_post_meta( $post_id, '_vacature_status', sanitize_text_field( $_POST['vacature_status'] ) );
    }
    if ( isset( $_POST['vacature_featured'] ) ) {
        update_post_meta( $post_id, '_vacature_featured', '1' );
    } else {
        update_post_meta( $post_id, '_vacature_featured', '0' );
    }

    // Save Testimonial meta
    if ( isset( $_POST['testimonial_author_name'] ) ) {
        update_post_meta( $post_id, '_testimonial_author_name', sanitize_text_field( $_POST['testimonial_author_name'] ) );
    }
    if ( isset( $_POST['testimonial_author_role'] ) ) {
        update_post_meta( $post_id, '_testimonial_author_role', sanitize_text_field( $_POST['testimonial_author_role'] ) );
    }
    if ( isset( $_POST['testimonial_featured'] ) ) {
        update_post_meta( $post_id, '_testimonial_featured', '1' );
    } else {
        update_post_meta( $post_id, '_testimonial_featured', '0' );
    }
}
add_action( 'save_post', 'stantonius_save_meta_boxes' );

/**
 * Register Custom Columns for CPTs
 */
function stantonius_custom_columns( $columns ) {

    // Activiteiten columns
    $columns['activiteiten'] = [
        'cb'            => '<input type="checkbox" />',
        'title'         => __( 'Titel', 'stantonius' ),
        'activiteit_date' => __( 'Datum', 'stantonius' ),
        'author'        => __( 'Auteur', 'stantonius' ),
        'categories'    => __( 'Categorie', 'stantonius' ),
    ];

    // Vacatures columns
    $columns['vacatures'] = [
        'cb'            => '<input type="checkbox" />',
        'title'         => __( 'Titel', 'stantonius' ),
        'location'      => __( 'Locatie', 'stantonius' ),
        'contract_type' => __( 'Contract', 'stantonius' ),
        'status'        => __( 'Status', 'stantonius' ),
        'author'        => __( 'Auteur', 'stantonius' ),
    ];

    // Testimonials columns
    $columns['testimonials'] = [
        'cb'            => '<input type="checkbox" />',
        'title'         => __( 'Titel', 'stantonius' ),
        'author_name'   => __( 'Naam', 'stantonius' ),
        'author_role'   => __( 'Rol', 'stantonius' ),
        'featured'      => __( 'Featured', 'stantonius' ),
    ];

    return $columns;
}
add_filter( 'manage_posts_columns', 'stantonius_custom_columns' );

/**
 * Populate Custom Columns
 */
function stantonius_populate_custom_columns( $column, $post_id ) {

    switch ( $column ) {

        case 'activiteit_date':
            $date = get_post_meta( $post_id, '_activiteit_date', true );
            echo $date ? esc_html( $date ) : __( '—', 'stantonius' );
            break;

        case 'location':
            $location = get_post_meta( $post_id, '_vacature_location', true );
            echo $location ? esc_html( $location ) : __( '—', 'stantonius' );
            break;

        case 'contract_type':
            $contract = get_post_meta( $post_id, '_vacature_contract_type', true );
            $types = [
                'voltijds'    => 'Voltijds',
                'deeltijds'   => 'Deeltijds',
                'dagdienst'   => 'Dagdienst',
                'nachtdienst' => 'Nachtdienst',
            ];
            echo $contract && isset( $types[ $contract ] ) ? esc_html( $types[ $contract ] ) : __( '—', 'stantonius' );
            break;

        case 'status':
            $status = get_post_meta( $post_id, '_vacature_status', true );
            $statuses = [
                'open'     => 'Open',
                'closed'   => 'Gesloten',
                'archived' => 'Gearchiveerd',
            ];
            echo $status && isset( $statuses[ $status ] ) ? esc_html( $statuses[ $status ] ) : __( '—', 'stantonius' );
            break;

        case 'author_name':
            $name = get_post_meta( $post_id, '_testimonial_author_name', true );
            echo $name ? esc_html( $name ) : __( '—', 'stantonius' );
            break;

        case 'author_role':
            $role = get_post_meta( $post_id, '_testimonial_author_role', true );
            echo $role ? esc_html( $role ) : __( '—', 'stantonius' );
            break;

        case 'featured':
            $featured = get_post_meta( $post_id, '_testimonial_featured', true );
            echo $featured === '1' ? __( 'Yes', 'stantonius' ) : __( '—', 'stantonius' );
            break;
    }
}
add_action( 'manage_posts_custom_column', 'stantonius_populate_custom_columns', 10, 2 );

/**
 * Make Custom Columns Sortable
 */
function stantonius_sortable_columns( $columns ) {

    $columns['activiteit_date'] = 'activiteit_date';
    $columns['location'] = 'location';
    $columns['contract_type'] = 'contract_type';
    $columns['status'] = 'status';
    $columns['author_name'] = 'author_name';
    $columns['author_role'] = 'author_role';
    $columns['featured'] = 'featured';

    return $columns;
}
add_filter( 'manage_edit-posts_sortable_columns', 'stantonius_sortable_columns' );

/**
 * Register Sidebar for CPT Admin
 */
function stantonius_register_admin_sidebars() {

    register_sidebar( [
        'name'          => __( 'CPT: Activiteiten Sidebar', 'stantonius' ),
        'id'            => 'sidebar-activiteiten',
        'description'   => __( 'Widgets for activiteiten single pages', 'stantonius' ),
        'before_widget' => '<section id="%1$s" class="widget %2$s">',
        'after_widget'  => '</section>',
        'before_title'  => '<h2 class="widget-title">',
        'after_title'   => '</h2>',
    ] );
}
add_action( 'widgets_init', 'stantonius_register_admin_sidebars' );

/**
 * Flush Rewrite Rules on Activation
 */
function stantonius_flush_rewrite_rules() {
    stantonius_register_cpts();
    stantonius_register_taxonomies();
    flush_rewrite_rules();
}
register_activation_hook( __FILE__, 'stantonius_flush_rewrite_rules' );

/**
 * Default Terms for Taxonomies
 */
function stantonius_add_default_terms() {

    // Default activiteit categories
    $activiteit_cats = [
        'Excursies',
        'Therapie',
        'Feestdagen',
        'Sport',
        'Creatief',
        'Maaltijden',
        'Gesprekken',
    ];

    foreach ( $activiteit_cats as $cat ) {
        if ( ! term_exists( $cat, 'activiteit_cat' ) ) {
            wp_insert_term( $cat, 'activiteit_cat' );
        }
    }

    // Default vacature categories
    $vacature_cats = [
        'Verpleging',
        'Zorg',
        'Administratie',
        'FDF',
        'Therapie',
    ];

    foreach ( $vacature_cats as $cat ) {
        if ( ! term_exists( $cat, 'vacature_cat' ) ) {
            wp_insert_term( $cat, 'vacature_cat' );
        }
    }

    // Default testimonial categories
    $testimonial_cats = [
        'Bewoner',
        'Familie',
        'Medewerker',
    ];

    foreach ( $testimonial_cats as $cat ) {
        if ( ! term_exists( $cat, 'testimonial_cat' ) ) {
            wp_insert_term( $cat, 'testimonial_cat' );
        }
    }
}
add_action( 'init', 'stantonius_add_default_terms' );
