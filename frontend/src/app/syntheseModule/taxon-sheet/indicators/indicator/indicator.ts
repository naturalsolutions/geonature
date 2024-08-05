export interface Indicator {
  name: string;
  matIcon: string;
  value: string | null;
}

const DEFAULT_VALUE = '-';

function getValue(field: string, unit: string | null, taxonStats: any) {
  if (taxonStats && taxonStats[field]) {
    return taxonStats[field] + unit ?? '';
  }
  return DEFAULT_VALUE;
}

export function computeIndicatorFromConfig(indicatorConfig: any, taxonStats: any): Indicator {
  return {
    name: indicatorConfig.name,
    matIcon: indicatorConfig.matIcon,
    value: taxonStats
      ? Array.isArray(indicatorConfig.field)
        ? indicatorConfig.field
            .map((field) => getValue(field, indicatorConfig.unit, taxonStats))
            .join(' - ')
        : getValue(indicatorConfig.field, indicatorConfig.unit, taxonStats)
      : DEFAULT_VALUE,
  };
}
