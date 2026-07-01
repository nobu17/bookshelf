import ApiBase from "./apibase";

type HealthResponse = {
  status: string;
};

const databaseStartupTimeoutMs = 120_000;

export default class HealthApi extends ApiBase {
  constructor() {
    super("", databaseStartupTimeoutMs);
  }

  async waitForDatabase(): Promise<void> {
    await this.getAsync<HealthResponse>("/health/db");
  }
}
