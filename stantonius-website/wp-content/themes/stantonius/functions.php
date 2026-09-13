<?php
/**
 * Theme Setup
 *
 * @package stantonius
 * @version 1.0.0
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Theme setup
 */
function stantonius_setup() {

    // Add default posts and comments RSS feed links to head
    add_theme_support( 'automatic-feed-links' );

    // Let WordPress manage the document title
    add_theme_support( 'title-tag' );

    // Enable support for Post Thumbnails
    add_theme_support( 'post-thumbnails' );

    // Register navigation menus
    register_nav_menus( [
        'primary' => __( 'Primary Menu', 'stantonius' ),
        'footer'  => __( 'Footer Menu', 'stantonius' ),
    ] );

    // Switch default core markup to output valid HTML5
    add_theme_support( 'html5', [
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
    ] );

    // Set up WordPress content width
    set_post_thumbnail_size( 1200, 800, true );

    // Add theme support for selective refresh for widgets
    add_theme_support( 'customize-selective-refresh-widgets' );
}
add_action( 'after_setup_theme', 'stantonius_setup' );

/**
 * Enqueue scripts and styles
 */
function stantonius_scripts() {
    wp_enqueue_style( 'stantonius-style', get_stylesheet_uri(), [], '1.0.0' );
    wp_enqueue_script( 'stantonius-scripts', get_template_directory_uri() . '/assets/js/main.js', [], '1.0.0', true );

    if ( is_singular() && comments_open() && get_option( 'thread_comments' ) ) {
        wp_enqueue_script( 'comment-reply' );
    }
}
add_action( 'wp_enqueue_scripts', 'stantonius_scripts' );

/**
 * Include custom files
 */
require get_template_directory() . '/inc/custom-post-types.php';
require get_template_directory() . '/inc/template-tags.php';
require get_template_directory() . '/inc/customizer.php';

/**
 * Customizer settings
 */
function stantonius_customize_register( $wp_customize ) {

    // Hero section
    $wp_customize->add_section( 'stantonius_hero', [
        'title'    => __( 'Hero Section', 'stantonius' ),
        'priority' => 30,
    ] );

    $wp_customize->add_setting( 'stantonius_hero_title', [
        'default'           => 'Wonen en leven onder de kerktoren',
        'sanitize_callback' => 'sanitize_text_field',
    ] );

    $wp_customize->add_control( 'stantonius_hero_title', [
        'label'   => __( 'Hero Title', 'stantonius' ),
        'section' => 'stantonius_hero',
        'type'    => 'text',
    ] );

    $wp_customize->add_setting( 'stantonius_hero_subtitle', [
        'default'           => 'Kwalitatief hoogstaande zorgverlening en een aangename leefomgeving op ieders maat',
        'sanitize_callback' => 'sanitize_textarea_field',
    ] );

    $wp_customize->add_control( 'stantonius_hero_subtitle', [
        'label'   => __( 'Hero Subtitle', 'stantonius' ),
        'section' => 'stantonius_hero',
        'type'    => 'textarea',
    ] );
}
add_action( 'customize_register', 'stantonius_customize_register' );
