/**
 * Owner Representation Profile — default preferences.
 *
 * No settings UI yet. Just a hardcoded default that the
 * NodeRenderer consults for view resolution. Future:
 * read from localStorage or API.
 */

import type { OwnerRepresentationProfile } from './types';

export const DEFAULT_PROFILE: OwnerRepresentationProfile = {
  id: 'leonardo-default',
  density: 'normal',
  layoutFamily: 'dashboard',
  motion: 'normal',
  defaultViews: {
    metric: 'gauge',
    status: 'status-pill',
    table: 'table',
    feed: 'feed',
    list: 'table',
    control: 'toggle',
    composite: 'composite',
  },
  renderer: 'react-tailwind',
};
