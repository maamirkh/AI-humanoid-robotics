import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Start Reading Textbook - 13 Weeks Journey ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

function ModuleGrid() {
  const modules = [
    {
      id: 1,
      title: 'Module 1: Foundations of Physical AI',
      description: 'Weeks 1-5: Explore the fundamentals of Physical AI, sensing, motor control, perception, and digital twins.',
      link: '/docs/module-1/week-1-foundations',
      color: 'primary'
    },
    {
      id: 2,
      title: 'Module 2: Digital Twin Concepts',
      description: 'Weeks 6-7: Understand physics simulation and human-robot interaction in digital environments.',
      link: '/docs/module-2/week-6-physics',
      color: 'secondary'
    },
    {
      id: 3,
      title: 'Module 3: Vision-Language-Action',
      description: 'Weeks 8-10: Master vision systems, mapping, and navigation for autonomous robots.',
      link: '/docs/module-3/week-8-vision',
      color: 'success'
    },
    {
      id: 4,
      title: 'Module 4: Complete Humanoid Systems',
      description: 'Weeks 11-13: Integrate all concepts into complete humanoid robotics systems.',
      link: '/docs/module-4/week-11-kinematics',
      color: 'info'
    }
  ];

  return (
    <section className={styles.modulesSection}>
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <Heading as="h2" className={clsx('margin-bottom--lg', styles.sectionTitle)}>
              Course Modules
            </Heading>
          </div>
        </div>
        <div className="row">
          {modules.map((module) => (
            <div className="col col--3 margin-bottom--lg" key={module.id}>
              <div className={clsx('card', styles.moduleCard)}>
                <div className="card__header">
                  <Heading as="h3">Module {module.id}</Heading>
                </div>
                <div className="card__body">
                  <h4>{module.title}</h4>
                  <p>{module.description}</p>
                </div>
                <div className="card__footer">
                  <Link
                    className={clsx('button', `button--${module.color}`, 'button--block')}
                    to={module.link}>
                    Start Module
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Physical AI & Humanoid Robotics Textbook">
      <HomepageHeader />
      <main>
        <ModuleGrid />
      </main>
    </Layout>
  );
}
