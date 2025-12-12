// @ts-check

/** @type {import("@docusaurus/plugin-content-docs").SidebarsConfig} */
const sidebars = {
  textbook: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro'],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 1: Foundations of Physical Intelligence',
      items: [
        'module-1/week-1-foundations',
        'module-1/week-2-sensing',
        'module-1/week-3-motor-control',
        'module-1/week-4-perception',
        'module-1/week-5-digital-twin',
        'module-1/summary',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 2: Physical Interaction & Human-Robot Dynamics',
      items: [
        'module-2/week-6-physics',
        'module-2/week-7-human-robot',
        'module-2/summary',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 3: Perception & Navigation',
      items: [
        'module-3/week-8-vision',
        'module-3/week-9-mapping',
        'module-3/week-10-navigation',
        'module-3/summary',
      ],
      collapsed: false,
    },
    {
      type: 'category',
      label: 'Module 4: Integration & System Design',
      items: [
        'module-4/week-11-kinematics',
        'module-4/week-12-decision',
        'module-4/week-13-system',
        'module-4/summary',
      ],
      collapsed: false,
    },
    {
      type: 'doc',
      id: 'capstone-project',
    },
    {
      type: 'doc',
      id: 'conclusion',
    },
  ],
};

module.exports = sidebars;
