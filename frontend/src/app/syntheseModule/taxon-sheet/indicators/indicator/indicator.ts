type IndicatorRawType = 'number' | 'string' | 'date';
export interface IndicatorRaw {
  name: string;
  matIcon: string;
  field: string | Array<string>;
  unit?: string;
  type: IndicatorRawType;
}

export interface Indicator {
  name: string;
  matIcon: string;
  value: string | null;
}

const DEFAULT_VALUE = '-';
const DEFAULT_SEPARATOR = ' - ';

function getValue(field: string, indicatorConfig: IndicatorRaw, taxonStats: any) {
  if (taxonStats && taxonStats[field]) {
    let valueAsString = '';
    switch (indicatorConfig.type) {
      case 'number':
        valueAsString = taxonStats[field].toLocaleString();
        break;
      case 'date':
        valueAsString = new Date(taxonStats[field]).toLocaleDateString();
        break;
      case 'string':
      default:
        valueAsString = taxonStats[field];
    }
    return valueAsString + (indicatorConfig.unit ?? '');
  }
  return DEFAULT_VALUE;
}

export function computeIndicatorFromConfig(
  indicatorConfig: IndicatorRaw,
  taxonStats: any
): Indicator {
  let value = DEFAULT_VALUE;
  if (taxonStats) {
    if (Array.isArray(indicatorConfig.field)) {
      value = indicatorConfig.field
        .map((field) => getValue(field, indicatorConfig, taxonStats))
        .join(DEFAULT_SEPARATOR);
    } else {
      value = getValue(indicatorConfig.field, indicatorConfig, taxonStats);
    }
  }
  return {
    name: indicatorConfig.name,
    matIcon: indicatorConfig.matIcon,
    value: value,
  };
}
