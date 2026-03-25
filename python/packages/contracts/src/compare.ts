import { z } from "zod";
import { areaMetricKeySchema, locationProfileSchema } from "./profile";

export const compareDeltaSchema = z.object({
  key: areaMetricKeySchema,
  label: z.string(),
  left: z.number(),
  right: z.number(),
  difference: z.number()
});

export const compareResponseSchema = z.object({
  left: locationProfileSchema,
  right: locationProfileSchema,
  deltas: z.array(compareDeltaSchema)
});

export type CompareResponse = z.infer<typeof compareResponseSchema>;
