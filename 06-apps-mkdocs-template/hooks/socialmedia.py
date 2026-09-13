"""MkDocs hook: add share buttons to blog posts."""

from textwrap import dedent
import urllib.parse
import re

x_intent = "https://x.com/intent/tweet"
linkedin_sharer = "https://www.linkedin.com/sharing/share-offsite/"
mastodon_sharer = "https://mastodon.social/share"
fb_sharer = "https://www.facebook.com/sharer/sharer.php"
include = re.compile(r"blog/[1-9].*")

ICON_X = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="16" height="16"><path d="M357.2 48h70.6L273.6 224.2 455 464H313L201.7 318.6 74.5 464H3.8l164.9-188.5L-5.2 48h145.6l100.5 132.9zm-24.8 373.8h39.1L119.1 88h-42z"/></svg>"""

ICON_LINKEDIN = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="16" height="16"><path d="M100.3 448H7.4V148.9h92.9zM53.8 108.1C24.1 108.1 0 83.5 0 53.8c0-14.3 5.7-27.9 15.8-38S39.6 0 53.8 0s27.9 5.7 38 15.8 15.8 23.8 15.8 38c0 29.7-24.1 54.3-53.8 54.3M447.9 448h-92.7V302.4c0-34.7-.7-79.2-48.3-79.2-48.3 0-55.7 37.7-55.7 76.7V448h-92.8V148.9h89.1v40.8h1.3c12.4-23.5 42.7-48.3 87.9-48.3 94 0 111.3 61.9 111.3 142.3V448z"/></svg>"""

ICON_MASTODON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512" width="16" height="16"><path d="M433 179.1c0-97.2-63.7-125.7-63.7-125.7-62.5-28.7-228.6-28.4-290.5 0 0 0-63.7 28.5-63.7 125.7 0 115.7-6.6 259.4 105.6 289.1 40.5 10.7 75.3 13 103.3 11.4 50.8-2.8 79.3-18.1 79.3-18.1l-1.7-36.9s-36.3 11.4-77.1 10.1c-40.4-1.4-83-4.4-89.6-54-.6-4.6-.9-9.3-.9-13.9 85.6 20.9 158.7 9.1 178.7 6.7 56.1-6.7 105-41.3 111.2-72.9 9.8-49.8 9-121.5 9-121.5zm-75.1 125.2h-46.6V190.1c0-49.7-64-51.6-64 6.9v62.5H201V197c0-58.5-64-56.6-64-6.9v114.2H90.3c0-122.1-5.2-147.9 18.4-175 25.9-28.9 79.8-30.8 103.8 6.1l11.6 19.5 11.6-19.5c24.1-37.1 78.1-34.8 103.8-6.1 23.7 27.3 18.4 53 18.4 175"/></svg>"""

ICON_FACEBOOK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="16" height="16"><path d="M512 256C512 114.6 397.4 0 256 0S0 114.6 0 256c0 120 82.7 220.8 194.2 248.5V334.2h-52.8V256h52.8v-33.7c0-87.1 39.4-127.5 125-127.5 16.2 0 44.2 3.2 55.7 6.4V172c-6-.6-16.5-1-29.6-1-42 0-58.2 15.9-58.2 57.2V256h83.6l-14.4 78.2H287v175.9C413.8 494.8 512 386.9 512 256"/></svg>"""


def on_page_markdown(markdown, **kwargs):
    page = kwargs["page"]
    config = kwargs["config"]
    if not include.match(page.url):
        return markdown

    page_url = config.site_url + page.url
    page_title = urllib.parse.quote(page.title + "\n")

    html = f"""\
    <p style="margin-top:1em;padding-top:.5em;border-top:1px solid var(--md-default-fg-color--lightest)">
      <a href="{x_intent}?text={page_title}&url={page_url}" target="_blank" rel="noopener" title="Share on X" style="margin-right:.5em;text-decoration:none;color:inherit">{ICON_X}</a>
      <a href="{linkedin_sharer}?url={page_url}" target="_blank" rel="noopener" title="Share on LinkedIn" style="margin-right:.5em;text-decoration:none;color:inherit">{ICON_LINKEDIN}</a>
      <a href="{mastodon_sharer}?text={page_title}&url={page_url}" target="_blank" rel="noopener" title="Share on Mastodon" style="margin-right:.5em;text-decoration:none;color:inherit">{ICON_MASTODON}</a>
      <a href="{fb_sharer}?u={page_url}" target="_blank" rel="noopener" title="Share on Facebook" style="margin-right:.5em;text-decoration:none;color:inherit">{ICON_FACEBOOK}</a>
    </p>
    """
    return markdown + dedent(html)
