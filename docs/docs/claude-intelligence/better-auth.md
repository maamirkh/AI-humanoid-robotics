# Better Auth Implementation for Physical AI & Humanoid Robotics Textbook

## Overview

This document outlines the implementation of Better Auth for the Physical AI & Humanoid Robotics Textbook project. Better Auth will provide user authentication and profile management to enable personalized learning experiences.

## Architecture

### 1. User Profile Schema

Better Auth will be configured with a custom user profile schema to capture relevant information for personalized learning:

```typescript
interface UserProfile {
  id: string;
  email: string;
  name: string;
  softwareBackground: {
    programmingLanguages: string[];
    frameworks: string[];
    experienceLevel: 'beginner' | 'intermediate' | 'advanced';
  };
  hardwareBackground: {
    roboticsExperience: boolean;
    electronicsKnowledge: 'none' | 'basic' | 'intermediate' | 'advanced';
    hasBuiltRobot: boolean;
  };
  educationalLevel: string;
  learningGoals: string[];
  createdAt: Date;
  preferences: {
    preferredLanguage: string;
    contentComplexity: 'beginner' | 'intermediate' | 'advanced';
    notificationSettings: {
      email: boolean;
      push: boolean;
    };
  };
}
```

### 2. Database Schema

Better Auth will use Neon Serverless Postgres for user data storage:

```sql
-- Users table (extended from Better Auth)
CREATE TABLE auth_user (
  id VARCHAR(255) PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT FALSE,
  name VARCHAR(255),
  image TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User profiles table
CREATE TABLE user_profiles (
  id VARCHAR(255) PRIMARY KEY,
  user_id VARCHAR(255) REFERENCES auth_user(id) ON DELETE CASCADE,
  software_background JSONB,
  hardware_background JSONB,
  educational_level VARCHAR(100),
  learning_goals TEXT[],
  preferences JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User activity tracking
CREATE TABLE user_activities (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(255) REFERENCES auth_user(id) ON DELETE CASCADE,
  module_id VARCHAR(100),
  chapter_id VARCHAR(100),
  completed BOOLEAN DEFAULT FALSE,
  progress_percentage INTEGER DEFAULT 0,
  last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  time_spent INTEGER -- in seconds
);
```

## Implementation Steps

### 1. Installation and Setup

```bash
npm install better-auth
```

### 2. Better Auth Configuration

Create the authentication configuration file:

```typescript
// src/auth/config.ts
import { betterAuth } from "better-auth";
import { postgresAdapter } from "better-auth/adapters/postgres";

export const auth = betterAuth({
  database: postgresAdapter({
    url: process.env.NEON_DATABASE_URL!,
    client: null, // Will use the existing Neon connection
  }),
  secret: process.env.AUTH_SECRET!,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  user: {
    additionalFields: {
      // Add custom fields for user profiles
    },
  },
  account: {
    accountLinking: {
      enabled: true,
      trustedProviders: ["google", "github"],
    },
  },
});
```

### 3. Custom User Profile Integration

Create a custom plugin to handle user profile data:

```typescript
// src/auth/plugins/user-profile.ts
import { plugin } from "better-auth";
import { neon } from "@neondatabase/serverless";

export const userProfilePlugin = plugin()({
  id: "user-profile",
  init: (ctx) => {
    return {
      $context: {
        async createUserProfile(userId: string, profileData: any) {
          const sql = neon(ctx.options.database.url);

          const result = await sql`
            INSERT INTO user_profiles (id, user_id, software_background, hardware_background, educational_level, learning_goals, preferences)
            VALUES (${userId}, ${userId}, ${JSON.stringify(profileData.softwareBackground)}, ${JSON.stringify(profileData.hardwareBackground)}, ${profileData.educationalLevel}, ${profileData.learningGoals}, ${JSON.stringify(profileData.preferences)})
            RETURNING *
          `;

          return result[0];
        },

        async getUserProfile(userId: string) {
          const sql = neon(ctx.options.database.url);

          const result = await sql`
            SELECT * FROM user_profiles WHERE user_id = ${userId}
          `;

          return result[0] || null;
        },

        async updateUserProfile(userId: string, profileData: any) {
          const sql = neon(ctx.options.database.url);

          const result = await sql`
            UPDATE user_profiles
            SET
              software_background = ${JSON.stringify(profileData.softwareBackground)},
              hardware_background = ${JSON.stringify(profileData.hardwareBackground)},
              educational_level = ${profileData.educationalLevel},
              learning_goals = ${profileData.learningGoals},
              preferences = ${JSON.stringify(profileData.preferences)},
              updated_at = NOW()
            WHERE user_id = ${userId}
            RETURNING *
          `;

          return result[0];
        },
      },
    };
  },
});
```

### 4. Client-Side Integration

Set up the client-side authentication:

```typescript
// src/auth/client.ts
import { createAuthClient } from "better-auth/react";
import { account } from "@better-auth/integrations/account";

export const { signIn, signOut, useSession } = createAuthClient({
  plugins: [account()],
});
```

### 5. Signup Process with Profile Collection

Create a signup flow that collects user background information:

```typescript
// src/components/auth/signup-with-profile.tsx
import { useState } from 'react';
import { authClient } from '../../auth/client';

export const SignupWithProfile = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    // Profile fields
    softwareExperience: 'beginner',
    programmingLanguages: [] as string[],
    hardwareExperience: 'none',
    roboticsExperience: false,
    educationalLevel: '',
    learningGoals: [] as string[],
  });

  const [step, setStep] = useState(1); // Multi-step form

  const handleSignup = async () => {
    try {
      // Step 1: Create user account
      const userResponse = await authClient.signUp.email({
        email: formData.email,
        password: formData.password,
        name: formData.name,
      });

      if (userResponse.error) {
        throw new Error(userResponse.error.message);
      }

      // Step 2: Create user profile
      const profileData = {
        softwareBackground: {
          programmingLanguages: formData.programmingLanguages,
          experienceLevel: formData.softwareExperience,
        },
        hardwareBackground: {
          roboticsExperience: formData.roboticsExperience,
          electronicsKnowledge: formData.hardwareExperience,
        },
        educationalLevel: formData.educationalLevel,
        learningGoals: formData.learningGoals,
        preferences: {
          preferredLanguage: 'en',
          contentComplexity: formData.softwareExperience,
          notificationSettings: {
            email: true,
            push: false,
          },
        },
      };

      // Send profile data to server action
      await fetch('/api/user-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: userResponse.data?.user.id,
          profileData,
        }),
      });

      // Redirect to dashboard or continue to textbook
    } catch (error) {
      console.error('Signup error:', error);
    }
  };

  return (
    <div className="signup-form">
      {step === 1 && (
        <div className="step-1">
          <h2>Account Information</h2>
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
          />
          {/* Additional account fields */}
          <button onClick={() => setStep(2)}>Next</button>
        </div>
      )}

      {step === 2 && (
        <div className="step-2">
          <h2>Tell us about your background</h2>
          {/* Software background questions */}
          <div>
            <label>Software Experience Level</label>
            <select
              value={formData.softwareExperience}
              onChange={(e) => setFormData({...formData, softwareExperience: e.target.value})}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          {/* Additional profile fields */}
          <button onClick={handleSignup}>Complete Signup</button>
        </div>
      )}
    </div>
  );
};
```

### 6. Signin Process

Implement the signin flow:

```typescript
// src/components/auth/signin.tsx
import { authClient } from '../../auth/client';

export const Signin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSignin = async () => {
    try {
      const response = await authClient.signIn.email({
        email,
        password,
      });

      if (response.error) {
        console.error('Signin error:', response.error.message);
        return;
      }

      // Redirect to dashboard or continue to textbook
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Signin error:', error);
    }
  };

  return (
    <div className="signin-form">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleSignin}>Sign In</button>

      {/* Social sign in options */}
      <button onClick={() => authClient.signIn.social({provider: 'google'})}>
        Sign in with Google
      </button>
      <button onClick={() => authClient.signIn.social({provider: 'github'})}>
        Sign in with GitHub
      </button>
    </div>
  );
};
```

## API Endpoints

### 1. User Profile Management

```typescript
// src/pages/api/user-profile.ts
import { auth } from '../../auth/config';
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const session = await auth.$ctx.getSessionFromHeaders({
    request: req as any,
  });

  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  switch (req.method) {
    case 'GET':
      // Get user profile
      const profile = await auth.$ctx.getUserProfile(session.user.id);
      return res.status(200).json(profile);

    case 'POST':
      // Create user profile
      const { profileData } = req.body;
      const newProfile = await auth.$ctx.createUserProfile(session.user.id, profileData);
      return res.status(201).json(newProfile);

    case 'PUT':
      // Update user profile
      const { profileData: updateData } = req.body;
      const updatedProfile = await auth.$ctx.updateUserProfile(session.user.id, updateData);
      return res.status(200).json(updatedProfile);

    default:
      res.setHeader('Allow', ['GET', 'POST', 'PUT']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

### 2. Profile Questionnaire

```typescript
// src/pages/api/profile-questionnaire.ts
import { auth } from '../../auth/config';
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const session = await auth.$ctx.getSessionFromHeaders({
    request: req as any,
  });

  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (req.method === 'GET') {
    // Return questionnaire questions
    const questionnaire = {
      softwareBackground: [
        {
          question: "What is your software development experience level?",
          type: "select",
          options: ["beginner", "intermediate", "advanced"],
          field: "experienceLevel"
        },
        {
          question: "Which programming languages are you familiar with?",
          type: "multiselect",
          options: ["Python", "C++", "ROS", "JavaScript", "Java", "Other"],
          field: "programmingLanguages"
        }
      ],
      hardwareBackground: [
        {
          question: "Do you have experience with robotics?",
          type: "boolean",
          field: "roboticsExperience"
        },
        {
          question: "What is your electronics knowledge level?",
          type: "select",
          options: ["none", "basic", "intermediate", "advanced"],
          field: "electronicsKnowledge"
        },
        {
          question: "Have you built a robot before?",
          type: "boolean",
          field: "hasBuiltRobot"
        }
      ],
      general: [
        {
          question: "What is your educational level?",
          type: "text",
          field: "educationalLevel"
        },
        {
          question: "What are your learning goals?",
          type: "textarea",
          field: "learningGoals"
        }
      ]
    };

    return res.status(200).json(questionnaire);
  }

  res.status(405).end(`Method ${req.method} Not Allowed`);
}
```

## Middleware for Protected Routes

```typescript
// src/middleware.ts
import { auth } from './auth/config';
import { NextRequest, NextResponse } from 'next/server';

export async function middleware(request: NextRequest) {
  const session = await auth.$ctx.getSessionFromHeaders({
    request: request as any,
  });

  // Protect certain routes
  if (request.nextUrl.pathname.startsWith('/personalize') && !session) {
    return NextResponse.redirect(new URL('/auth/signin', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/personalize/:path*', '/profile/:path*'],
};
```

## Environment Variables

Create a `.env.local` file with the required environment variables:

```bash
# Better Auth
AUTH_SECRET=your-super-secret-auth-key-here
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
BETTER_AUTH_URL=http://localhost:3000

# Database
NEON_DATABASE_URL=your-neon-database-url

# Social Providers (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Integration with Textbook Features

### 1. Personalized Content Delivery

```typescript
// src/utils/personalization.ts
import { auth } from '../auth/config';

export async function getPersonalizedContent(userId: string, contentId: string) {
  const profile = await auth.$ctx.getUserProfile(userId);

  if (!profile) {
    // Return default content if no profile
    return await getDefaultContent(contentId);
  }

  // Adjust content based on user profile
  const originalContent = await getDefaultContent(contentId);

  return customizeContentForUser(originalContent, profile);
}

function customizeContentForUser(content: string, profile: any) {
  // Adjust complexity based on experience level
  if (profile.softwareBackground.experienceLevel === 'beginner') {
    // Add more explanations and examples
    return addBeginnerExplanations(content);
  } else if (profile.softwareBackground.experienceLevel === 'advanced') {
    // Skip basic explanations
    return skipBasicExplanations(content);
  }

  return content;
}
```

## Security Considerations

1. **Data Protection**: User profile data is stored securely in Neon Postgres
2. **Authentication**: All API endpoints are protected with Better Auth session validation
3. **Privacy**: User data is only used for personalization purposes
4. **Compliance**: GDPR and other privacy regulations compliance

## Deployment

1. Set up Neon Serverless Postgres database
2. Configure environment variables
3. Deploy Better Auth endpoints
4. Test authentication flow
5. Verify user profile collection and storage