export type DisplayOption = {
  isDisplayComplete: boolean;
  isDisplayInProgress: boolean;
  isDisplayNotYet: boolean;
  order: DisplayOrderOption;
};

export const DisplayOrderOptionDef = {
  CompletedDesc: 0,
  CompletedAsc: 1,
  EditedDesc: 2,
  EditedAsc: 3,
} as const;


export type DisplayOrderOption =
  (typeof DisplayOrderOptionDef)[keyof typeof DisplayOrderOptionDef];

export const toJapanese = (displayOrder: DisplayOrderOption): string => {
  switch (displayOrder) {
    case DisplayOrderOptionDef.CompletedDesc:
      return "読了順(新)";
    case DisplayOrderOptionDef.CompletedAsc:
      return "読了順(古)";
    case DisplayOrderOptionDef.EditedDesc:
      return "編集順(新)";
    case DisplayOrderOptionDef.EditedAsc:
      return "編集順(古)";
  }
}

export const AllFilterConditions: DisplayOrderOption[] = [
  DisplayOrderOptionDef.CompletedDesc,
  DisplayOrderOptionDef.CompletedAsc,
  DisplayOrderOptionDef.EditedDesc,
  DisplayOrderOptionDef.EditedAsc,
];
