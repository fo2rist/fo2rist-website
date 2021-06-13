[![Netlify Status](https://api.netlify.com/api/v1/badges/d7a76aea-fa65-4f15-bf40-f03f31ff21de/deploy-status)](https://app.netlify.com/sites/fo2rist/deploys)

# t-kittens.fo2rist.com site

Originally based on based on Hugo Novela Forestry Starter
## Prerequisites

- Hugo > 0.55.0

## Deployment and hosting with Netlify

Import your site in [Netlify](https://netlify.com)

1. Create a new site in Netlify and import your repository.
2. Set the build command to: `hugo --gc --minify`
3. Set the publish directory to: `public`
4. Make sure to set `HUGO_VERSION` to 0.55.0 or above

That's it, now your site gets deployed automatically on `git push` or when saving documents from Forestry.

## Development

```bash
# Start local dev server
hugo server
```

For more information, see [official Hugo documentation](https://gohugo.io/getting-started/).

## Customization

### Logo

Add to your projects layout directory your logo's SVG:
`/layouts/icons/ui/logo.html`

### Socials

In order for the Socials to be surfaced in Forestry, you should copy the theme's `config/_default/social.yaml` to your project.

### Authors

You should register authors as a taxonomy in your project's `config.yaml``

```yaml
taxonomies:
  author: authors
```

#### Creating authors

Add a similar file to your content directory and Front Matter example.

```yaml
# /content/authors/firstname-lastname/_index.md
---
title: Dmitry Sitnikov
bio: |
  Written by You. This is where your author bio lives.
avatar: /images/dima.jpeg
featured: true
social:
  - title: github
    url: https://github.com
  - title: twitter
    url: https://twitter.com
  - title: instagram
    url: https://instagram.com
---
```

#### Assigning authors to posts.
Add the name of the author to the "authors" field:

```yaml
authors:
  - Dmitry Sitnikov
  - George Ymydykov
  - Yulia Terterian
```
### Newsletter call to action

This theme includes a shortcode for a newsletter callout form that you can add to any page.
It uses [formspree.io](//formspree.io/) as proxy to send the actual email. Each month, visitors can send you up to one thousand emails without incurring extra charges. Visit the Formspree site to get get going add your Formspree email to your shortcode like this:

```
{{< subscribe email="your@email.com" >}}
```

## LICENSE

MIT
