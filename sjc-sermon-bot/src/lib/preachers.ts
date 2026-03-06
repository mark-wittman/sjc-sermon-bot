export interface PreacherInfo {
  name: string;
  slug: string;
  role: string;
  color: string;
  colorLight: string;
}

export const PREACHERS: Record<string, PreacherInfo> = {
  "Richard Lawson": {
    name: "Richard Lawson",
    slug: "richard-lawson",
    role: "Dean",
    color: "#7D1721",
    colorLight: "#f2e0e2",
  },
  "Katie Pearson": {
    name: "Katie Pearson",
    slug: "katie-pearson",
    role: "Canon for Formation",
    color: "#1B4D6E",
    colorLight: "#dfe9f0",
  },
  "Broderick Greer": {
    name: "Broderick Greer",
    slug: "broderick-greer",
    role: "Canon Precentor",
    color: "#2D5A27",
    colorLight: "#e0eedf",
  },
  "Jack Karn": {
    name: "Jack Karn",
    slug: "jack-karn",
    role: "Curate",
    color: "#6B4C8A",
    colorLight: "#ece5f2",
  },
  "Deonna Neal": {
    name: "Deonna Neal",
    slug: "deonna-neal",
    role: "Theologian in Residence",
    color: "#8B6914",
    colorLight: "#f2ecdb",
  },
  "Paul Keene": {
    name: "Paul Keene",
    slug: "paul-keene",
    role: "Assisting Priest",
    color: "#1A5C5C",
    colorLight: "#dfefef",
  },
};

export function getPreacherBySlug(slug: string): PreacherInfo | undefined {
  return Object.values(PREACHERS).find((p) => p.slug === slug);
}

export function getPreacherByName(name: string): PreacherInfo | undefined {
  return PREACHERS[name];
}

export function getPreacherColor(name: string): string {
  return PREACHERS[name]?.color || "#7D1721";
}
