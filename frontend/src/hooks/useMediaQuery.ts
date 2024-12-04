import { useState, useEffect, useCallback } from 'react';

const MOBILE_BREAKPOINT = 768;

/**
 * Custom hook for handling media queries
 * @param query The media query to check
 * @returns A boolean indicating whether the media query matches
 */
const useMediaQuery = (query: string): boolean => {
  const getMatches = useCallback((query: string): boolean => {
    // Check if window is available (for SSR)
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  }, []);

  const [matches, setMatches] = useState<boolean>(getMatches(query));

  useEffect(() => {
    const handleChange = () => setMatches(getMatches(query));

    const matchMedia = window.matchMedia(query);

    // Triggered at the first client-side load and if query changes
    handleChange();

    // Use addListener and removeListener for wider browser support
    if (matchMedia.addListener) {
      matchMedia.addListener(handleChange);
    } else {
      matchMedia.addEventListener('change', handleChange);
    }

    return () => {
      if (matchMedia.removeListener) {
        matchMedia.removeListener(handleChange);
      } else {
        matchMedia.removeEventListener('change', handleChange);
      }
    };
  }, [query, getMatches]);

  return matches;
};

export default useMediaQuery;

/**
 * Hook to check if the current viewport is desktop size
 * @returns A boolean indicating if the viewport is desktop size
 */
export const useIsDesktop = (): boolean =>
  useMediaQuery(`(min-width: ${MOBILE_BREAKPOINT}px)`);

/**
 * Hook to check if the current viewport is mobile size
 * @returns A boolean indicating if the viewport is mobile size
 */
export const useIsMobile = (): boolean =>
  useMediaQuery(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
