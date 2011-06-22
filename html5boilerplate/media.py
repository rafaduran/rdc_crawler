# Usage:

# Either use this file wholesale:

# from mediagenerator_boilerplate.media import HTML5_MEDIA_BUNDLES
# MEDIA_BUNDLES += HTML5_MEDIA_BUNDLES

# Or copy the required parts from below to your MEDIA_BUNDLES in settings.py

HTML5_MEDIA_BUNDLES = (
    ('style.css',
        'css/style.css',
    ),

    ('head.js',
        'js/libs/modernizr-2.0.js',
        'js/libs/respond.js',
    ),

    ('main.js',
        {'filter': 'mediagenerator.filters.media_url.MediaURL'},
        'js/libs/jquery-1.6.1.js',
        'js/plugins.js',
        'js/script.js',
    ),
)
