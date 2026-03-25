import { z } from "zod";

export const sourceSchema = z.enum(["fixture", "pdok"]);
export const placeTypeSchema = z.enum(["adres", "pand", "wijk", "gemeente", "unknown"]);

export const suggestResultSchema = z.object({
  id: z.string(),
  label: z.string(),
  type: placeTypeSchema,
  lat: z.number().nullable(),
  lon: z.number().nullable(),
  source: sourceSchema
});

export const suggestResponseSchema = z.object({
  query: z.string(),
  results: z.array(suggestResultSchema)
});

export const resolvedAddressSchema = z.object({
  street: z.string().nullable(),
  houseNumber: z.string().nullable(),
  houseLetter: z.string().nullable(),
  houseNumberSuffix: z.string().nullable(),
  postalCode: z.string().nullable(),
  city: z.string().nullable()
});

export const areaCodesSchema = z.object({
  buurtCode: z.string().nullable(),
  wijkCode: z.string().nullable(),
  gemeenteCode: z.string().nullable()
});

export const resolvedPlaceSchema = z.object({
  id: z.string(),
  label: z.string(),
  type: placeTypeSchema,
  lat: z.number().nullable(),
  lon: z.number().nullable(),
  address: resolvedAddressSchema.nullable(),
  areaCodes: areaCodesSchema.nullable(),
  source: sourceSchema
});

export type PlaceType = z.infer<typeof placeTypeSchema>;
export type SuggestResult = z.infer<typeof suggestResultSchema>;
export type SuggestResponse = z.infer<typeof suggestResponseSchema>;
export type ResolvedPlace = z.infer<typeof resolvedPlaceSchema>;
