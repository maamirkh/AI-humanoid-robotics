// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  textbookSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro'],
    },
    {
      type: 'category',
      label: 'Module 1: Foundations of Physical AI',
      items: [
        'module-1/week-1-foundations',
        'module-1/week-2-sensing',
        'module-1/week-3-motor-control',
        'module-1/week-4-perception',
        'module-1/week-5-digital-twin',
        'module-1/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twin Concepts',
      items: [
        'module-2/week-6-physics',
        'module-2/week-7-human-robot',
        'module-2/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: Vision-Language-Action',
      items: [
        'module-3/week-8-vision',
        'module-3/week-9-mapping',
        'module-3/week-10-navigation',
        'module-3/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Complete Humanoid Systems',
      items: [
        'module-4/week-11-kinematics',
        'module-4/week-12-decision',
        'module-4/week-13-system',
        'module-4/summary',
      ],
    },
    {
      type: 'category',
      label: 'Conclusion: The Future of Physical AI and Humanoid Robotics',
      items: [
        'conclusion',
      ],
    },
  ],
};

export default sidebars;
