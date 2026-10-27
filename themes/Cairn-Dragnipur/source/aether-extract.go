package main

import (
	"aether/internal/extraction"
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	if len(os.Args) != 2 {
		panic("Expected wallpaper path")
	}
	dominant, counts, err := extraction.ExtractDominantColors(os.Args[1], extraction.DominantColorsToExtract)
	if err != nil {
		panic(err)
	}
	total := 0
	for _, n := range counts {
		total += n
	}
	weights := make([]float64, len(counts))
	for i, n := range counts {
		weights[i] = float64(n) / float64(total)
	}
	result := map[string]interface{}{"source": "Aether 29d07b1a8f474c77bf02aece948373f40abed105", "dominant": dominant, "counts": counts}
	for _, mode := range []string{"normal", "muted"} {
		result[mode+"_dark"] = extraction.NormalizeBrightness(extraction.GeneratePaletteByMode(dominant, weights, false, mode))
	}
	result["normal_light"] = extraction.NormalizeBrightness(extraction.GeneratePaletteByMode(dominant, weights, true, "normal"))
	output, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		panic(err)
	}
	fmt.Println(string(output))
}
