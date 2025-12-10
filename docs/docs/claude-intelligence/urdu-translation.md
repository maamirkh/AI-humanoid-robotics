# Urdu Translation Toggle Implementation for Physical AI & Humanoid Robotics Textbook

## Overview

This document outlines the implementation of a Urdu translation feature for the Physical AI & Humanoid Robotics Textbook. The feature will allow logged-in users to toggle between English and Urdu content on a per-chapter basis, preserving formatting and technical terms while providing accurate translations.

## Architecture

### 1. Translation Service Architecture

The Urdu translation feature consists of multiple components working together:

```typescript
interface TranslationService {
  translateContent(text: string, targetLanguage: string): Promise<string>;
  cacheTranslation(key: string, translation: string): Promise<void>;
  getCachedTranslation(key: string): Promise<string | null>;
  detectLanguage(text: string): Promise<string>;
}

interface TranslationToggle {
  toggleLanguage(contentId: string, targetLanguage: string): Promise<TranslatedContent>;
  getAvailableLanguages(contentId: string): Promise<string[]>;
  saveUserPreference(userId: string, language: string): Promise<void>;
  getUserPreference(userId: string): Promise<string>;
}
```

### 2. Content Structure

The translation system will work with the existing Docusaurus content structure:

```
docs/
├── module-1/
│   ├── week-1-foundations.md (English)
│   ├── week-1-foundations.ur.md (Urdu)
│   └── ...
├── module-2/
│   ├── week-6-physics.md (English)
│   ├── week-6-physics.ur.md (Urdu)
│   └── ...
└── ...
```

## Implementation Components

### 1. Translation API Service

```typescript
// src/services/translation-service.ts
import { GoogleGenerativeAI } from "@google/generative-ai";

export class TranslationService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor() {
    this.genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);
    this.model = this.genAI.getGenerativeModel({ model: "gemini-pro" });
  }

  async translateContent(text: string, targetLanguage: string = "ur"): Promise<string> {
    // Preserve code blocks, mathematical formulas, and technical terms
    const { preserved, placeholders } = this.preserveSpecialContent(text);

    // Create translation prompt with specific instructions for technical content
    const prompt = `
      Translate the following English text to ${this.getLanguageName(targetLanguage)}.
      Preserve the meaning and technical accuracy.
      Keep all code blocks, file paths, technical terms, and mathematical formulas in English.
      Do not translate proper nouns, programming language names, or technical terminology.

      Text to translate:
      ${preserved}
    `;

    try {
      const result = await this.model.generateContent(prompt);
      let translated = result.response.text();

      // Restore preserved content
      translated = this.restoreSpecialContent(translated, placeholders);

      return translated;
    } catch (error) {
      console.error('Translation error:', error);
      throw new Error('Failed to translate content');
    }
  }

  private preserveSpecialContent(text: string): { preserved: string; placeholders: Map<string, string> } {
    const placeholders = new Map<string, string>();
    let preserved = text;

    // Preserve code blocks
    const codeBlockRegex = /(```[\s\S]*?```|`[^`]*`)/g;
    let match;
    let index = 0;

    while ((match = codeBlockRegex.exec(preserved)) !== null) {
      const placeholder = `__CODE_BLOCK_${index}__`;
      placeholders.set(placeholder, match[0]);
      preserved = preserved.replace(match[0], placeholder);
      index++;
    }

    // Preserve inline math and formulas
    const mathRegex = /(\$\$[\s\S]*?\$\$|\$[^$]*\$)/g;
    while ((match = mathRegex.exec(preserved)) !== null) {
      const placeholder = `__MATH_${index}__`;
      placeholders.set(placeholder, match[0]);
      preserved = preserved.replace(match[0], placeholder);
      index++;
    }

    // Preserve technical terms in brackets or specific formats
    const techTermRegex = /(\[[^\]]+\]|<[^>]+>)/g;
    while ((match = techTermRegex.exec(preserved)) !== null) {
      const placeholder = `__TECH_TERM_${index}__`;
      placeholders.set(placeholder, match[0]);
      preserved = preserved.replace(match[0], placeholder);
      index++;
    }

    return { preserved, placeholders };
  }

  private restoreSpecialContent(text: string, placeholders: Map<string, string>): string {
    let restored = text;

    for (const [placeholder, original] of placeholders) {
      restored = restored.replace(new RegExp(placeholder, 'g'), original);
    }

    return restored;
  }

  private getLanguageName(languageCode: string): string {
    const languages: { [key: string]: string } = {
      'ur': 'Urdu',
      'en': 'English'
    };
    return languages[languageCode] || languageCode;
  }
}
```

### 2. Translation Cache Service

```typescript
// src/services/translation-cache.ts
import NodeCache from 'node-cache';

export class TranslationCache {
  private cache: NodeCache;

  constructor() {
    // Cache translations for 24 hours
    this.cache = new NodeCache({ stdTTL: 86400 });
  }

  async getTranslation(contentId: string, targetLanguage: string): Promise<string | null> {
    const cacheKey = `${contentId}:${targetLanguage}`;
    return this.cache.get(cacheKey);
  }

  async setTranslation(contentId: string, targetLanguage: string, translation: string): Promise<void> {
    const cacheKey = `${contentId}:${targetLanguage}`;
    this.cache.set(cacheKey, translation);
  }

  async invalidate(contentId: string, targetLanguage: string): Promise<void> {
    const cacheKey = `${contentId}:${targetLanguage}`;
    this.cache.del(cacheKey);
  }

  async invalidateAllForContent(contentId: string): Promise<void> {
    const keys = this.cache.keys().filter(key => key.startsWith(contentId + ':'));
    this.cache.del(keys);
  }
}
```

### 3. Frontend Translation Toggle Component

```tsx
// src/components/translation/translation-toggle.tsx
import { useState, useEffect } from 'react';
import { useSession } from '../../auth/client';
import { TranslationService } from '../../services/translation-service';

interface TranslationToggleProps {
  contentId: string;
  children: string; // The English content
}

export const TranslationToggle = ({ contentId, children }: TranslationToggleProps) => {
  const { data: session } = useSession();
  const [currentContent, setCurrentContent] = useState(children);
  const [isTranslated, setIsTranslated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [userLanguage, setUserLanguage] = useState('en');

  const translateToUrdu = async () => {
    if (!session) {
      alert('Please log in to use translation feature');
      return;
    }

    setIsLoading(true);
    try {
      const service = new TranslationService();
      const translatedContent = await service.translateContent(children, 'ur');
      setCurrentContent(translatedContent);
      setIsTranslated(true);
      setUserLanguage('ur');

      // Save user preference
      if (session.user.id) {
        await saveUserLanguagePreference(session.user.id, 'ur');
      }
    } catch (error) {
      console.error('Translation error:', error);
      alert('Failed to translate content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const translateToEnglish = () => {
    setCurrentContent(children);
    setIsTranslated(false);
    setUserLanguage('en');

    if (session?.user.id) {
      saveUserLanguagePreference(session.user.id, 'en');
    }
  };

  const toggleLanguage = () => {
    if (isTranslated) {
      translateToEnglish();
    } else {
      translateToUrdu();
    }
  };

  // Load user's language preference on mount
  useEffect(() => {
    if (session?.user.id) {
      loadUserLanguagePreference(session.user.id);
    }
  }, [session]);

  const loadUserLanguagePreference = async (userId: string) => {
    try {
      const response = await fetch(`/api/user-preferences/${userId}/language`);
      if (response.ok) {
        const { language } = await response.json();
        if (language === 'ur' && !isTranslated) {
          // Auto-translate if user prefers Urdu
          translateToUrdu();
        }
      }
    } catch (error) {
      console.error('Error loading language preference:', error);
    }
  };

  const saveUserLanguagePreference = async (userId: string, language: string) => {
    try {
      await fetch(`/api/user-preferences/${userId}/language`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language }),
      });
    } catch (error) {
      console.error('Error saving language preference:', error);
    }
  };

  return (
    <div className="translation-container">
      <div className="translation-controls">
        <button
          onClick={toggleLanguage}
          disabled={isLoading}
          className={`translation-toggle-btn ${isTranslated ? 'urdu-mode' : 'english-mode'}`}
        >
          {isLoading ? (
            'Translating...'
          ) : isTranslated ? (
            'English'
          ) : (
            'اردو'
          )}
        </button>

        {isTranslated && (
          <span className="translation-indicator">
            ترجمہ کردہ مواد
          </span>
        )}
      </div>

      <div
        className={`translated-content ${isTranslated ? 'urdu-text' : 'english-text'}`}
        dir={isTranslated ? 'rtl' : 'ltr'}
      >
        {currentContent}
      </div>
    </div>
  );
};
```

### 4. Translation API Endpoints

```typescript
// src/pages/api/translation/[contentId].ts
import { auth } from '../../../auth/config';
import { TranslationService } from '../../../services/translation-service';
import { TranslationCache } from '../../../services/translation-cache';
import { NextApiRequest, NextApiResponse } from 'next';

const translationService = new TranslationService();
const cache = new TranslationCache();

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const session = await auth.$ctx.getSessionFromHeaders({
    request: req as any,
  });

  if (!session) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const { contentId } = req.query;
  const { sourceContent, targetLanguage = 'ur' } = req.body;

  switch (req.method) {
    case 'POST':
      try {
        // Check cache first
        let translation = await cache.getTranslation(contentId as string, targetLanguage as string);

        if (!translation) {
          // Translate content if not in cache
          translation = await translationService.translateContent(sourceContent, targetLanguage as string);

          // Cache the translation
          await cache.setTranslation(contentId as string, targetLanguage as string, translation);
        }

        return res.status(200).json({
          translatedContent: translation,
          sourceLanguage: 'en',
          targetLanguage
        });
      } catch (error) {
        console.error('Translation API error:', error);
        return res.status(500).json({ error: 'Translation failed' });
      }

    case 'DELETE':
      // Clear cache for this content
      try {
        await cache.invalidateAllForContent(contentId as string);
        return res.status(200).json({ message: 'Translation cache cleared' });
      } catch (error) {
        console.error('Cache clear error:', error);
        return res.status(500).json({ error: 'Failed to clear cache' });
      }

    default:
      res.setHeader('Allow', ['POST', 'DELETE']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

### 5. User Language Preference API

```typescript
// src/pages/api/user-preferences/[userId]/language.ts
import { auth } from '../../../../auth/config';
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const session = await auth.$ctx.getSessionFromHeaders({
    request: req as any,
  });

  if (!session || session.user.id !== req.query.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const userId = req.query.userId as string;

  switch (req.method) {
    case 'GET':
      try {
        // Get user's language preference from their profile
        const profile = await auth.$ctx.getUserProfile(userId);
        const language = profile?.preferences?.preferredLanguage || 'en';

        return res.status(200).json({ language });
      } catch (error) {
        console.error('Get language preference error:', error);
        return res.status(500).json({ error: 'Failed to get language preference' });
      }

    case 'PUT':
      try {
        const { language } = req.body;

        if (!language || !['en', 'ur'].includes(language)) {
          return res.status(400).json({ error: 'Invalid language code' });
        }

        // Update user's language preference in their profile
        const profile = await auth.$ctx.getUserProfile(userId);
        const updatedProfile = {
          ...profile,
          preferences: {
            ...profile?.preferences,
            preferredLanguage: language
          }
        };

        await auth.$ctx.updateUserProfile(userId, updatedProfile);

        return res.status(200).json({ message: 'Language preference updated' });
      } catch (error) {
        console.error('Update language preference error:', error);
        return res.status(500).json({ error: 'Failed to update language preference' });
      }

    default:
      res.setHeader('Allow', ['GET', 'PUT']);
      res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
```

## Docusaurus Integration

### 1. Translation-aware MDX Component

```tsx
// src/docusaurus-plugin/translation/components/TranslationWrapper.tsx
import React, { useState, useEffect } from 'react';
import { TranslationToggle } from '../../../components/translation/translation-toggle';

interface TranslationWrapperProps {
  children: React.ReactNode;
  contentId: string;
}

export const TranslationWrapper: React.FC<TranslationWrapperProps> = ({
  children,
  contentId
}) => {
  const [content, setContent] = useState('');

  useEffect(() => {
    // Extract text content from MDX children
    const extractText = (node: React.ReactNode): string => {
      if (typeof node === 'string') {
        return node;
      }

      if (React.isValidElement(node)) {
        if (node.type === 'code' || node.type === 'pre') {
          // Preserve code blocks as-is
          return node.props.children || '';
        }

        if (node.props && node.props.children) {
          return React.Children.map(node.props.children, extractText)?.join(' ') || '';
        }
      }

      if (Array.isArray(node)) {
        return node.map(extractText).join(' ');
      }

      return '';
    };

    const textContent = extractText(children);
    setContent(textContent);
  }, [children]);

  return (
    <div className="translation-wrapper">
      <TranslationToggle contentId={contentId} children={content} />
      <div className="original-content">
        {children}
      </div>
    </div>
  );
};
```

### 2. Docusaurus Plugin for Translation

```typescript
// src/docusaurus-plugin/translation/index.js
module.exports = function(context, options) {
  return {
    name: 'docusaurus-plugin-translation',

    async contentLoaded({ actions }) {
      const { setGlobalData } = actions;

      // Set global data for translation features
      setGlobalData({
        enableTranslation: true,
        supportedLanguages: ['en', 'ur'],
        defaultLanguage: 'en',
        translationApiUrl: process.env.TRANSLATION_API_URL || '/api/translation'
      });
    },

    configureWebpack(config, isServer, utils) {
      return {
        plugins: [
          // Add any webpack plugins needed for translation
        ],
      };
    },

    // Extend the default Docusaurus lifecycle
    plugins: [
      // Additional plugins for translation features
    ]
  };
};
```

### 3. Right-to-Left (RTL) Styling

```css
/* src/css/translation-styles.css */
.translation-container {
  position: relative;
  margin: 1rem 0;
}

.translation-controls {
  margin-bottom: 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.translation-toggle-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.2s ease;
}

.translation-toggle-btn:hover {
  background: #e0e0e0;
}

.translation-toggle-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.translation-indicator {
  font-size: 0.8rem;
  color: #666;
  padding: 0.25rem 0.5rem;
  background: #e8f4fd;
  border-radius: 4px;
}

/* Urdu text styling */
.urdu-text {
  font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Urdu Typesetting', serif;
  direction: rtl;
  text-align: right;
  line-height: 1.8;
}

.english-text {
  font-family: inherit;
  direction: ltr;
  text-align: left;
}

/* Responsive design for translation */
@media (max-width: 768px) {
  .translation-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .translation-toggle-btn {
    width: 100%;
  }
}
```

## Advanced Translation Features

### 1. Batch Translation Service

```typescript
// src/services/batch-translation.ts
export class BatchTranslationService {
  async translateModule(moduleId: string, targetLanguage: string): Promise<TranslationResult[]> {
    // Get all content files for the module
    const contentFiles = await this.getContentFilesForModule(moduleId);

    const results: TranslationResult[] = [];

    // Process each file
    for (const file of contentFiles) {
      try {
        const translation = await this.translateFile(file, targetLanguage);
        results.push(translation);
      } catch (error) {
        console.error(`Failed to translate ${file.path}:`, error);
        results.push({
          filePath: file.path,
          success: false,
          error: error.message
        });
      }
    }

    return results;
  }

  private async translateFile(file: ContentFile, targetLanguage: string): Promise<TranslationResult> {
    const translationService = new TranslationService();
    const content = await this.readFileContent(file.path);

    const translatedContent = await translationService.translateContent(content, targetLanguage);

    // Save translated content
    const translatedFilePath = this.getTranslatedFilePath(file.path, targetLanguage);
    await this.saveFileContent(translatedFilePath, translatedContent);

    return {
      filePath: file.path,
      translatedFilePath,
      success: true
    };
  }

  private getTranslatedFilePath(originalPath: string, targetLanguage: string): string {
    const pathParts = originalPath.split('.');
    pathParts.splice(-1, 0, targetLanguage); // Insert language code before extension
    return pathParts.join('.');
  }
}
```

### 2. Translation Quality Assurance

```typescript
// src/services/translation-quality.ts
export class TranslationQualityService {
  async validateTranslation(original: string, translated: string, targetLanguage: string): Promise<ValidationResult> {
    const issues: string[] = [];

    // Check for preserved content
    const originalCodeBlocks = this.extractCodeBlocks(original);
    const translatedCodeBlocks = this.extractCodeBlocks(translated);

    if (originalCodeBlocks.length !== translatedCodeBlocks.length) {
      issues.push('Code blocks mismatch');
    } else {
      for (let i = 0; i < originalCodeBlocks.length; i++) {
        if (originalCodeBlocks[i] !== translatedCodeBlocks[i]) {
          issues.push(`Code block ${i} was modified`);
        }
      }
    }

    // Check for technical term preservation
    const originalTechTerms = this.extractTechnicalTerms(original);
    const translatedTechTerms = this.extractTechnicalTerms(translated);

    for (const term of originalTechTerms) {
      if (!translated.includes(term)) {
        issues.push(`Technical term "${term}" was translated`);
      }
    }

    // Check content length (should be roughly similar for technical content)
    const lengthRatio = translated.length / original.length;
    if (lengthRatio < 0.5 || lengthRatio > 2.0) {
      issues.push('Significant length discrepancy');
    }

    return {
      isValid: issues.length === 0,
      issues,
      score: this.calculateQualityScore(original, translated, issues)
    };
  }

  private extractCodeBlocks(text: string): string[] {
    const codeBlockRegex = /(```[\s\S]*?```|`[^`]*`)/g;
    const matches = text.match(codeBlockRegex) || [];
    return matches;
  }

  private extractTechnicalTerms(text: string): string[] {
    // Extract terms that should not be translated
    const techTerms = [
      'AI', 'API', 'ROS', 'Python', 'C++', 'JavaScript', 'Node.js', 'Docusaurus',
      'TensorFlow', 'PyTorch', 'algorithm', 'function', 'variable', 'class',
      'object', 'method', 'parameter', 'interface', 'framework', 'library',
      'module', 'package', 'import', 'export', 'async', 'await', 'Promise'
    ];

    return techTerms.filter(term => text.includes(term));
  }

  private calculateQualityScore(original: string, translated: string, issues: string[]): number {
    // Base score calculation
    let score = 100;

    // Deduct points for each issue
    score -= issues.length * 10;

    // Adjust for length discrepancy
    const lengthRatio = translated.length / original.length;
    if (lengthRatio < 0.7 || lengthRatio > 1.3) {
      score -= 15;
    }

    return Math.max(0, score);
  }
}
```

## Performance Optimization

### 1. Translation Caching Strategy

```typescript
// src/services/translation-cache.ts (enhanced)
import Redis from 'ioredis';

export class AdvancedTranslationCache {
  private redis: Redis;

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
  }

  async getTranslation(contentId: string, targetLanguage: string): Promise<string | null> {
    const cacheKey = `translation:${contentId}:${targetLanguage}`;
    const cached = await this.redis.get(cacheKey);

    if (cached) {
      // Also cache in memory for faster access
      await this.cacheInMemory(cacheKey, cached);
    }

    return cached;
  }

  async setTranslation(contentId: string, targetLanguage: string, translation: string): Promise<void> {
    const cacheKey = `translation:${contentId}:${targetLanguage}`;

    // Set in Redis with 24-hour expiration
    await this.redis.setex(cacheKey, 86400, translation);

    // Also cache in memory
    await this.cacheInMemory(cacheKey, translation);
  }

  private async cacheInMemory(cacheKey: string, translation: string): Promise<void> {
    // Implement in-memory caching for frequently accessed translations
    // This could use a library like node-cache or similar
  }
}
```

### 2. Translation Progress Tracking

```typescript
// src/services/translation-progress.ts
export class TranslationProgressService {
  async trackProgress(userId: string, contentId: string, progress: number): Promise<void> {
    // Track user's progress in translation
    await this.updateUserTranslationProgress(userId, contentId, progress);

    // Update content statistics
    await this.updateContentTranslationStats(contentId);
  }

  private async updateUserTranslationProgress(userId: string, contentId: string, progress: number): Promise<void> {
    // Update user's translation progress in the database
    const db = getDatabaseConnection();

    await db.query(`
      INSERT INTO user_translation_progress (user_id, content_id, progress, last_updated)
      VALUES ($1, $2, $3, NOW())
      ON CONFLICT (user_id, content_id)
      DO UPDATE SET progress = $3, last_updated = NOW()
    `, [userId, contentId, progress]);
  }

  private async updateContentTranslationStats(contentId: string): Promise<void> {
    // Update statistics about how many users have translated this content
    const db = getDatabaseConnection();

    await db.query(`
      INSERT INTO content_translation_stats (content_id, translation_count, last_updated)
      VALUES ($1, 1, NOW())
      ON CONFLICT (content_id)
      DO UPDATE SET translation_count = content_translation_stats.translation_count + 1, last_updated = NOW()
    `, [contentId]);
  }
}
```

## Security Considerations

### 1. Rate Limiting for Translation API

```typescript
// src/middleware/translation-ratelimit.ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "10s"), // 10 translations per 10 seconds per user
});

export async function checkTranslationRateLimit(userId: string): Promise<{ success: boolean; message?: string }> {
  const result = await ratelimit.limit(`translation_${userId}`);

  if (!result.success) {
    return {
      success: false,
      message: "Translation rate limit exceeded. Please wait before translating more content."
    };
  }

  return { success: true };
}
```

### 2. Content Sanitization

```typescript
// src/services/content-sanitizer.ts
import DOMPurify from 'isomorphic-dompurify';

export class ContentSanitizer {
  sanitizeTranslatedContent(content: string): string {
    // Sanitize HTML content to prevent XSS
    return DOMPurify.sanitize(content, {
      ALLOWED_TAGS: ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 'code', 'pre', 'a', 'blockquote', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
      ALLOWED_ATTR: ['href', 'target', 'rel', 'class', 'id']
    });
  }
}
```

## Testing Strategy

### 1. Translation Unit Tests

```typescript
// tests/translation-service.test.ts
import { TranslationService } from '../src/services/translation-service';

describe('TranslationService', () => {
  let service: TranslationService;

  beforeEach(() => {
    service = new TranslationService();
  });

  test('should preserve code blocks during translation', async () => {
    const original = `Here is some code: \`\`\`python\nprint("Hello World")\n\`\`\``;
    const translated = await service.translateContent(original, 'ur');

    expect(translated).toContain('print("Hello World")');
    expect(translated).toContain('Hello World');
  });

  test('should preserve technical terms', async () => {
    const original = 'The AI algorithm uses Python and TensorFlow';
    const translated = await service.translateContent(original, 'ur');

    expect(translated).toContain('AI');
    expect(translated).toContain('Python');
    expect(translated).toContain('TensorFlow');
  });

  test('should handle mathematical formulas', async () => {
    const original = 'The equation is $E = mc^2$';
    const translated = await service.translateContent(original, 'ur');

    expect(translated).toContain('$E = mc^2$');
  });
});
```

### 2. Integration Tests

```typescript
// tests/translation-api.test.ts
import request from 'supertest';
import app from '../src/app';

describe('Translation API', () => {
  test('POST /api/translation/:contentId should translate content', async () => {
    const response = await request(app)
      .post('/api/translation/test-content')
      .set('Authorization', 'Bearer valid-token')
      .send({
        sourceContent: 'Hello, this is a test',
        targetLanguage: 'ur'
      });

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('translatedContent');
    expect(response.body.targetLanguage).toBe('ur');
  });

  test('should require authentication', async () => {
    const response = await request(app)
      .post('/api/translation/test-content')
      .send({
        sourceContent: 'Hello, this is a test',
        targetLanguage: 'ur'
      });

    expect(response.status).toBe(401);
  });
});
```

## Deployment Configuration

### 1. Environment Variables

```bash
# Translation API
GEMINI_API_KEY=your-gemini-api-key
TRANSLATION_API_URL=https://your-domain.com/api/translation
TRANSLATION_CACHE_TTL=86400

# Caching
REDIS_URL=your-redis-url

# Rate limiting
UPSTASH_REDIS_REST_URL=your-upstash-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-token
```

### 2. CDN Configuration for Translated Content

```javascript
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/_next/static/translation/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

This implementation provides a comprehensive Urdu translation toggle feature that integrates seamlessly with the Docusaurus-based Physical AI & Humanoid Robotics textbook, preserving technical content while providing accurate translations for educational purposes.