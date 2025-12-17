// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import("@docusaurus/types").Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Bridging Digital Intelligence with Physical Reality',
  // favicon: 'img/favicon.ico', // Removed since favicon file was deleted

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<basePath>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'maamirkh', // Usually your GitHub org/user name.
  projectName: 'physical-ai-humanoid-robotics', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  markdown: {
    mermaid: true,
    mdx1Compat: {
      comments: true,
      admonitions: true,
      headingIds: true,
    },
  },

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import("@docusaurus/preset-classic").Options} */
      ({
        docs: {
          path: '.',  // Look for docs in the current directory
          routeBasePath: '/', // Serve docs at the root route
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/maamirkh/AI-humanoid-robotics/tree/main/',
          // Exclude node_modules from being processed
          exclude: ['node_modules/**'],
        },
        blog: false, // Disable the blog plugin since blog files were removed
        theme: {
          // customCss: './src/css/custom.css', // Removed since CSS file was deleted
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import("@docusaurus/preset-classic").ThemeConfig} */
    ({
      backendUrl: process.env.BACKEND_URL || 'https://mamir1983-rag-docusaurus-book.hf.space',
      // image: 'img/docusaurus-social-card.jpg', // Removed since image file was deleted
      navbar: {
        title: 'Physical AI & Humanoid Robotics',
        // logo: {
        //   alt: 'Physical AI Logo',
        //   src: 'img/logo.svg', // Removed since logo file was deleted
        // },
        items: [
          {
            type: 'doc',
            docId: 'intro',
            position: 'left',
            label: 'Textbook',
          },
          {
            href: 'https://github.com/maamirkh/AI-humanoid-robotics',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Textbook',
            items: [
              {
                label: 'Introduction',
                to: '/intro',
              },
              {
                label: 'Module 1: Foundations',
                to: '/module-1/week-1-foundations',
              },
              {
                label: 'Module 2: Interaction',
                to: '/module-2/week-6-physics',
              },
              {
                label: 'Module 3: Perception & Navigation',
                to: '/module-3/week-8-vision',
              },
              {
                label: 'Module 2: Interaction',
                to: '/module-2/week-6-physics',
              },
              {
                label: 'Module 3: Perception & Navigation',
                to: '/module-3/week-8-vision',
              },
              {
                label: 'Module 4: Integration',
                to: '/module-4/week-11-kinematics',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/maamirkh/AI-humanoid-robotics',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Module 4: Integration',
                to: '/module-4/week-11-kinematics',
                label: 'Physical AI Capstone',
                to: '/capstone-project',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/maamirkh/AI-humanoid-robotics',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Physical AI Capstone',
                to: '/capstone-project',
              },
              {
                label: 'Conclusion',
                to: '/conclusion',
              },
            ],
          },
        ],
        copyright: `Copyright © \${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
    plugins: [
      async function configureHtmlTags(context, options) {
        return {
          name: 'html-tags-config',
          injectHtmlTags() {
            return {
              headTags: [
                {
                  tagName: 'script',
                  innerHTML: `window.CHATBOT_BACKEND_URL = '${process.env.BACKEND_URL || 'https://mamir1983-rag-docusaurus-book.hf.space'}';`,
                },
              ],
            };
          },
        };
      },
    ],
    scripts: [
      {
        src: '/js/config.js',
        async: true,
      },
    ],
};

export default config;