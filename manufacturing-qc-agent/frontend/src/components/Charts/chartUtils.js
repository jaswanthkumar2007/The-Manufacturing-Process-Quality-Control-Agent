/**
 * Shared chart utilities and default threshold constants.
 */
export const THRESHOLDS_DEFAULT = {
  temperature: { ucl: 80,    lcl: 20   },
  pressure:    { ucl: 9.5,   lcl: 1.5  },
  vibration:   { ucl: 4.5,   lcl: 0    },
  humidity:    { ucl: 65,    lcl: 35   },
  speed:       { ucl: 2800,  lcl: 150  },
  defect_rate: { ucl: 3.0,   lcl: 0    },
  torque:      { ucl: 95,    lcl: 6    },
  flow_rate:   { ucl: 18,    lcl: 1    },
};

export const SENSOR_UNITS = {
  temperature: '°C',
  pressure:    'bar',
  vibration:   'mm/s',
  humidity:    '%RH',
  speed:       'RPM',
  defect_rate: '%',
  torque:      'N·m',
  flow_rate:   'L/min',
};

export const SENSOR_COLORS = {
  temperature: '#f59e0b',
  pressure:    '#3b82f6',
  vibration:   '#ef4444',
  humidity:    '#06b6d4',
  speed:       '#8b5cf6',
  defect_rate: '#ec4899',
  torque:      '#10b981',
  flow_rate:   '#f97316',
};
