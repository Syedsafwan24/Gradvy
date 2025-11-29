// /home/mohammed-azaan-peshmam/Desktop/Gradvy/Project/Gradvy/frontend/src/config/env.js
// Environment variable validation using Zod
// Validates NEXT_PUBLIC_API_URL and provides type-safe access
// RELEVANT FILES: api.js, ../lib/api.js, .env.local.example, DEVELOPER_GUIDE.md

import { z } from 'zod';

// Schema for environment variables
const envSchema = z.object({
  NEXT_PUBLIC_API_URL: z
    .string()
    .url('NEXT_PUBLIC_API_URL must be a valid URL')
    .refine(
      (url) => !url.endsWith('/'),
      'NEXT_PUBLIC_API_URL should not end with / (it will be added automatically)'
    ),
});

// Validate and parse environment variables
function validateEnv() {
  const parsed = envSchema.safeParse({
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  });

  if (!parsed.success) {
    console.error('❌ Invalid environment variables:');
    console.error(parsed.error.flatten().fieldErrors);
    console.error('\n📝 Please check your .env.local file and ensure:');
    console.error('   1. NEXT_PUBLIC_API_URL is set');
    console.error('   2. It is a valid URL (e.g., http://localhost:8030)');
    console.error('   3. It does not end with a trailing slash');
    console.error('\n💡 Example: NEXT_PUBLIC_API_URL=http://localhost:8030\n');
    throw new Error('Invalid environment configuration. Check .env.local file.');
  }

  return parsed.data;
}

// Export validated environment variables
export const env = validateEnv();

// Type-safe access to API URL
export const API_URL = env.NEXT_PUBLIC_API_URL;
