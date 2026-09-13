<?php
/**
 * Polylang Integration for CPTs
 *
 * Registers CPTs and taxonomies for translation
 * Requires: Polylang plugin
 *
 * @package stantonius
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Register CPTs for Polylang
 */
function stantonius_polylang_register_strings() {

    // CPT Labels - Activities
    pll_register_string( 'stantonius_activiteiten_name', 'Activiteiten', 'stantonius' );
    pll_register_string( 'stantonius_activiteiten_singular', 'Activiteit', 'stantonius' );
    pll_register_string( 'stantonius_activiteiten_add_new', 'Nieuwe activiteit', 'stantonius' );
    pll_register_string( 'stantonius_activiteiten_description', 'Blog-style posts for activity reports with photos', 'stantonius' );

    // CPT Labels - Vacancies
    pll_register_string( 'stantonius_vacatures_name', 'Vacatures', 'stantonius' );
    pll_register_string( 'stantonius_vacatures_singular', 'Vacature', 'stantonius' );
    pll_register_string( 'stantonius_vacatures_add_new', 'Nieuwe vacature', 'stantonius' );
    pll_register_string( 'stantonius_vacatures_description', 'Job listings with application form integration', 'stantonius' );

    // CPT Labels - Testimonials
    pll_register_string( 'stantonius_testimonials_name', 'Testimonials', 'stantonius' );
    pll_register_string( 'stantonius_testimonials_singular', 'Testimonial', 'stantonius' );
    pll_register_string( 'stantonius_testimonials_add_new', 'Nieuw testimonial', 'stantonius' );
    pll_register_string( 'stantonius_testimonials_description', 'Quotes from residents and family members', 'stantonius' );

    // Taxonomy Labels - Activiteit
    pll_register_string( 'stantonius_activiteit_cat_name', 'Activiteit Categorieën', 'stantonius' );
    pll_register_string( 'stantonius_excursies', 'Excursies', 'stantonius' );
    pll_register_string( 'stantonius_therapie', 'Therapie', 'stantonius' );
    pll_register_string( 'stantonius_feestdagen', 'Feestdagen', 'stantonius' );
    pll_register_string( 'stantonius_sport', 'Sport', 'stantonius' );

    // Taxonomy Labels - Vacature
    pll_register_string( 'stantonius_vacature_cat_name', 'Vacature Categorieën', 'stantonius' );
    pll_register_string( 'stantonius_verpleging', 'Verpleging', 'stantonius' );
    pll_register_string( 'stantonius_zorg', 'Zorg', 'stantonius' );
    pll_register_string( 'stantonius_administratie', 'Administratie', 'stantonius' );

    // Taxonomy Labels - Testimonial
    pll_register_string( 'stantonius_testimonial_cat_name', 'Testimonial Categorieën', 'stantonius' );
    pll_register_string( 'stantonius_bewoner', 'Bewoner', 'stantonius' );
    pll_register_string( 'stantonius_familie', 'Familie', 'stantonius' );
    pll_register_string( 'stantonius_medewerker', 'Medewerker', 'stantonius' );

    // Meta field labels
    pll_register_string( 'stantonius_meta_activiteit_date', 'Activiteit Datum', 'stantonius' );
    pll_register_string( 'stantonius_meta_location', 'Locatie', 'stantonius' );
    pll_register_string( 'stantonius_meta_contract', 'Contracttype', 'stantonius' );
    pll_register_string( 'stantonius_meta_author', 'Naam', 'stantonius' );
    pll_register_string( 'stantonius_meta_role', 'Rol', 'stantonius' );
}
add_action( 'init', 'stantonius_polylang_register_strings' );

/**
 * Add CPTs to Polylang post types
 */
function stantonius_polylang_setup() {

    if ( function_exists( 'pll_register_post_type' ) ) {
        // Register post types for translation
        pll_register_post_type( 'activiteiten', [ 'post_types' => true, 'taxonomies' => true ] );
        pll_register_post_type( 'vacatures', [ 'post_types' => true, 'taxonomies' => true ] );
        pll_register_post_type( 'testimonials', [ 'post_types' => true, 'taxonomies' => true ] );

        // Register taxonomies for translation
        pll_register_taxonomy( 'activiteit_cat' );
        pll_register_taxonomy( 'vacature_cat' );
        pll_register_taxonomy( 'testimonial_cat' );
    }

    if ( function_exists( 'icl_register_string' ) ) {
        // WPML equivalent - already handled by pll_register_string above
    }
}
add_action( 'after_setup_theme', 'stantonius_polylang_setup' );
