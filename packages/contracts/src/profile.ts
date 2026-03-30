import { z } from "zod";
import { resolvedPlaceSchema } from "./place";

export const areaMetricKeySchema = z.enum([
  "population",
  "households",
  "housingStock",
  "avgWozX1000Eur",
  "ownerOccupiedPct",
  "rentalPct",
  "densityPerKm2",
  "solarPct",
  "gasFreePct"
]);

export const buildingSchema = z.object({
  yearBuilt: z.number().nullable(),
  usageType: z.string().nullable(),
  floorAreaM2: z.number().nullable()
});

export const areaMetricsSchema = z.object({
  population: z.number().nullable(),
  households: z.number().nullable(),
  housingStock: z.number().nullable(),
  avgWozX1000Eur: z.number().nullable(),
  ownerOccupiedPct: z.number().nullable(),
  rentalPct: z.number().nullable(),
  densityPerKm2: z.number().nullable(),
  solarPct: z.number().nullable(),
  gasFreePct: z.number().nullable()
});

export const sourceBreakdownSchema = z.object({
  place: z.enum(["fixture", "pdok"]),
  building: z.enum(["fixture", "bag", "none"]),
  metrics: z.enum(["fixture", "cbs", "none"])
});

export const locationProfileSchema = z.object({
  place: resolvedPlaceSchema,
  building: buildingSchema,
  areaMetrics: areaMetricsSchema,
  sourceBreakdown: sourceBreakdownSchema
});

export type AreaMetricKey = z.infer<typeof areaMetricKeySchema>;
export type AreaMetrics = z.infer<typeof areaMetricsSchema>;
export type Building = z.infer<typeof buildingSchema>;
export type LocationProfile = z.infer<typeof locationProfileSchema>;
