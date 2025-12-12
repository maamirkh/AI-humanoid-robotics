import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--primary button--lg"
            to="/intro">
            Start Reading Book
          </Link>
        </div>
      </div>
    </header>
  );
}

function ModuleCard({ title, description, to, colorClass }) {
  const handleMouseEnter = (e) => {
    const card = e.currentTarget.querySelector('.card');
    if (card) {
      card.style.transform = 'translateY(-10px)';
      card.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.25)';
      card.style.transition = 'all 0.3s ease';
    }
    // Additional effects can be added here
    const titleElement = e.currentTarget.querySelector(`.${styles.moduleTitle}`);
    if (titleElement) {
      titleElement.style.color = '#2a7df0';
    }
  };

  const handleMouseLeave = (e) => {
    const card = e.currentTarget.querySelector('.card');
    if (card) {
      card.style.transform = 'translateY(0)';
      card.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.18)';
    }
    // Reset title color
    const titleElement = e.currentTarget.querySelector(`.${styles.moduleTitle}`);
    if (titleElement) {
      titleElement.style.color = '#25c2a0';
    }
  };

  return (
    <div className={styles.moduleCol} onMouseEnter={handleMouseEnter} onMouseLeave={handleMouseLeave}>
      <div className="card">
        <div className="card__body">
          <h3 className={styles.moduleTitle}>{title}</h3>
          <p>{description}</p>
        </div>
        <div className="card__footer">
          <Link className={`button ${colorClass} button--block`} to={to}>
            Explore Module
          </Link>
        </div>
      </div>
    </div>
  );
}

function ModuleGrid() {
  return (
    <section className={styles.modules}>
      <div className="container">
        <div className={styles.moduleRow}>
          <ModuleCard
            title="Module 1: Foundations"
            description="Physical AI and embodied intelligence, Digital AI to robots understanding physical laws, Humanoid robotics landscape and concepts"
            to="/module-1/week-1-foundations"
            colorClass="button--primary"
          />
          <ModuleCard
            title="Module 2: Interaction"
            description="Sensor systems (LIDAR, cameras, IMUs, force/torque sensors), How physical systems perceive, Core principles of embodied cognition"
            to="/module-2/week-6-physics"
            colorClass="button--secondary"
          />
          <ModuleCard
            title="Module 3: Perception & Navigation"
            description="Gazebo simulation environment setup, URDF and SDF formats, Physics simulation and sensor simulation"
            to="/module-3/week-8-vision"
            colorClass="button--success"
          />
          <ModuleCard
            title="Module 4: Integration"
            description="Humanoid robot kinematics and dynamics, Bipedal locomotion and balance control, Manipulation and grasping"
            to="/module-4/week-11-kinematics"
            colorClass="button--info"
          />
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Bridging Digital Intelligence with Physical Reality">
      <HomepageHeader />
      <main>
        <ModuleGrid />
      </main>
    </Layout>
  );
}