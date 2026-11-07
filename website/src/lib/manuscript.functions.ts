import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

export const examineSyntheticManuscript = createServerFn({ method: "POST" })
  .validator((input: unknown) =>
    z
      .object({
        fixture: z.enum(["faint-stroke-v1", "blank-v1", "noise-v1", "overlap-v1"]),
      })
      .parse(input),
  )
  .handler(async ({ data }) => {
    const { currentManuscriptConfig, examineManuscriptFixture } = await import("./manuscript.server");
    return examineManuscriptFixture(currentManuscriptConfig(), data.fixture);
  });
