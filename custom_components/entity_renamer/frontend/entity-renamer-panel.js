import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class EntityRenamerPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
      entities: { type: Array },
      filteredEntities: { type: Array },
      selectedEntities: { type: Array },
      suggestions: { type: Array },
      loading: { type: Boolean },
      suggestionsLoading: { type: Boolean },
      searchTerm: { type: String },
      filterArea: { type: String },
      filterDevice: { type: String },
      message: { type: String },
      messageType: { type: String },
      areas: { type: Array },
      devices: { type: Array },
    };
  }

  constructor() {
    super();
    this.entities = [];
    this.filteredEntities = [];
    this.selectedEntities = [];
    this.suggestions = [];
    this.loading = true;
    this.suggestionsLoading = false;
    this.searchTerm = "";
    this.filterArea = "";
    this.filterDevice = "";
    this.message = "";
    this.messageType = "info";
    this.areas = [];
    this.devices = [];
  }

  connectedCallback() {
    super.connectedCallback();
    this.loadEntities();
  }

  async loadEntities() {
    this.loading = true;
    try {
      const headers = {};
      if (this.hass && this.hass.auth && this.hass.auth.accessToken) {
        headers["Authorization"] = `Bearer ${this.hass.auth.accessToken}`;
      }
      const response = await fetch("/api/entity_renamer/entities", {
        headers,
      });
      if (response.ok) {
        const data = await response.json();
        this.entities = data;
        this.filteredEntities = [...data];

        // Extract unique areas and devices for filters
        const areaSet = new Set();
        const deviceSet = new Set();

        this.entities.forEach(entity => {
          if (entity.area_name) areaSet.add(entity.area_name);
          if (entity.device_name) deviceSet.add(entity.device_name);
        });

        this.areas = Array.from(areaSet).sort();
        this.devices = Array.from(deviceSet).sort();
      } else {
        this.showMessage("Failed to load entities", "error");
      }
    } catch (error) {
      this.showMessage(`Error: ${error.message}`, "error");
    } finally {
      this.loading = false;
    }
  }

  applyFilters() {
    this.filteredEntities = this.entities.filter(entity => {
      const matchesSearch = !this.searchTerm ||
        entity.entity_id.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        (entity.name && entity.name.toLowerCase().includes(this.searchTerm.toLowerCase()));

      const matchesArea = !this.filterArea || entity.area_name === this.filterArea;
      const matchesDevice = !this.filterDevice || entity.device_name === this.filterDevice;

      return matchesSearch && matchesArea && matchesDevice;
    });
  }

  handleSearchInput(e) {
    this.searchTerm = e.target.value;
    this.applyFilters();
  }

  handleAreaFilter(e) {
    this.filterArea = e.target.value;
    this.applyFilters();
  }

  handleDeviceFilter(e) {
    this.filterDevice = e.target.value;
    this.applyFilters();
  }

  toggleSelectEntity(entity) {
    const index = this.selectedEntities.findIndex(e => e.entity_id === entity.entity_id);
    if (index === -1) {
      this.selectedEntities = [...this.selectedEntities, entity];
    } else {
      this.selectedEntities = this.selectedEntities.filter(e => e.entity_id !== entity.entity_id);
    }
  }

  selectAll() {
    this.selectedEntities = [...this.filteredEntities];
  }

  clearSelection() {
    this.selectedEntities = [];
  }

  toggleSelectGroup(groupEntities, checked) {
    if (checked) {
      const newEntities = groupEntities.filter(
        (e) => !this.selectedEntities.some((se) => se.entity_id === e.entity_id)
      );
      this.selectedEntities = [...this.selectedEntities, ...newEntities];
    } else {
      const ids = new Set(groupEntities.map((e) => e.entity_id));
      this.selectedEntities = this.selectedEntities.filter(
        (e) => !ids.has(e.entity_id)
      );
    }
  }

  groupEntitiesByArea() {
    const groups = {};
    for (const entity of this.filteredEntities) {
      const area = entity.area_name || "No Area";
      if (!groups[area]) groups[area] = [];
      groups[area].push(entity);
    }
    return Object.entries(groups).sort((a, b) => a[0].localeCompare(b[0]));
  }

  toFriendlyName(entityId) {
    const [, namePart] = entityId.split(".");
    const base = namePart || entityId;
    return base
      .split("_")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  async getSuggestions() {
    if (this.selectedEntities.length === 0) {
      this.showMessage("Please select at least one entity", "warning");
      return;
    }

    this.suggestionsLoading = true;
    this.suggestions = [];

    try {
      const headers = {
        "Content-Type": "application/json",
      };
      if (this.hass && this.hass.auth && this.hass.auth.accessToken) {
        headers["Authorization"] = `Bearer ${this.hass.auth.accessToken}`;
      }
      const response = await fetch("/api/entity_renamer/suggest", {
        method: "POST",
        headers,
        body: JSON.stringify({
          entities: this.selectedEntities,
        }),
      });

      const data = await response.json();

      if (data.success) {
        this.suggestions = data.suggestions.map(s => ({
          ...s,
          suggested_name: s.suggested_name || this.toFriendlyName(s.suggested_id),
        }));
        this.showMessage("Suggestions received successfully", "success");
      } else {
        this.showMessage(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      this.showMessage(`Error: ${error.message}`, "error");
    } finally {
      this.suggestionsLoading = false;
    }
  }

  async applyRename(entity, suggestedId, suggestedName) {
    try {
      const headers = {
        "Content-Type": "application/json",
      };
      if (this.hass && this.hass.auth && this.hass.auth.accessToken) {
        headers["Authorization"] = `Bearer ${this.hass.auth.accessToken}`;
      }
      const response = await fetch("/api/entity_renamer/rename", {
        method: "POST",
        headers,
        body: JSON.stringify({
          entity_id: entity.entity_id,
          new_entity_id: suggestedId,
          new_name: suggestedName,
        }),
      });

      const data = await response.json();

      if (data.success) {
        // Update the entity in our local list
        const updatedEntities = this.entities.map((e) => {
          if (e.entity_id === entity.entity_id) {
            return { ...e, entity_id: suggestedId, name: suggestedName };
          }
          return e;
        });

        this.entities = updatedEntities;
        this.applyFilters();

        // Remove from suggestions
        this.suggestions = this.suggestions.filter(
          (s) => s.entity_id !== entity.entity_id
        );

        this.showMessage(
          `Renamed ${entity.entity_id} successfully`,
          "success"
        );
      } else {
        this.showMessage(`Error: ${data.error}`, "error");
      }
    } catch (error) {
      this.showMessage(`Error: ${error.message}`, "error");
    }
  }

  async applyAllSuggestions() {
    if (this.suggestions.length === 0) {
      this.showMessage("No suggestions to apply", "warning");
      return;
    }

    const headers = {
      "Content-Type": "application/json",
    };
    if (this.hass && this.hass.auth && this.hass.auth.accessToken) {
      headers["Authorization"] = `Bearer ${this.hass.auth.accessToken}`;
    }
    const promises = this.suggestions.map((suggestion) =>
      fetch("/api/entity_renamer/rename", {
        method: "POST",
        headers,
        body: JSON.stringify({
          entity_id: suggestion.entity_id,
          new_entity_id: suggestion.suggested_id,
          new_name: suggestion.suggested_name,
        }),
      })
    );

    try {
      const results = await Promise.all(promises);
      const allSuccessful = results.every(r => r.ok);

      if (allSuccessful) {
        // Update all entities in our local list
        const updatedEntities = this.entities.map((entity) => {
          const suggestion = this.suggestions.find(
            (s) => s.entity_id === entity.entity_id
          );
          if (suggestion) {
            return {
              ...entity,
              entity_id: suggestion.suggested_id,
              name: suggestion.suggested_name,
            };
          }
          return entity;
        });

        this.entities = updatedEntities;
        this.applyFilters();

        // Clear suggestions
        this.suggestions = [];

        this.showMessage("All suggestions applied successfully", "success");
      } else {
        this.showMessage("Some renames failed, please try again", "error");
      }
    } catch (error) {
      this.showMessage(`Error: ${error.message}`, "error");
    }
  }

  showMessage(message, type = "info") {
    this.message = message;
    this.messageType = type;

    // Clear message after 5 seconds
    setTimeout(() => {
      this.message = "";
    }, 5000);
  }

  render() {
    return html`
      <ha-card header="AI Entity Renamer">
        <div class="card-content">
          ${this.message ? html`
            <div class="message ${this.messageType}">
              ${this.message}
            </div>
          ` : ""}

          <div class="filters">
            <div class="search-box">
              <ha-icon icon="mdi:magnify"></ha-icon>
              <input
                type="text"
                placeholder="Search entities..."
                @input=${this.handleSearchInput}
                .value=${this.searchTerm}
              />
            </div>

            <div class="filter-selects">
              <select @change=${this.handleAreaFilter} .value=${this.filterArea}>
                <option value="">All Areas</option>
                ${this.areas.map(area => html`
                  <option value=${area}>${area}</option>
                `)}
              </select>

              <select @change=${this.handleDeviceFilter} .value=${this.filterDevice}>
                <option value="">All Devices</option>
                ${this.devices.map(device => html`
                  <option value=${device}>${device}</option>
                `)}
              </select>
            </div>
          </div>

          ${this.loading ? html`
            <div class="loading">
              <ha-circular-progress active></ha-circular-progress>
              <p>Loading entities...</p>
            </div>
          ` : html`
            <div class="entity-table-container">
              <div class="select-all-row">
                <input
                  type="checkbox"
                  ?checked=${this.selectedEntities.length === this.filteredEntities.length && this.filteredEntities.length > 0}
                  @change=${() => this.selectedEntities.length === this.filteredEntities.length ? this.clearSelection() : this.selectAll()}
                />
                <span>Select All</span>
              </div>

              ${this.filteredEntities.length === 0
                ? html`<div class="no-entities">No entities found</div>`
                : this.groupEntitiesByArea().map(([area, entities]) => html`
                    <details class="area-group" open>
                      <summary>
                        <input
                          type="checkbox"
                          ?checked=${entities.every(e => this.selectedEntities.some(se => se.entity_id === e.entity_id))}
                          @change=${(e) => this.toggleSelectGroup(entities, e.target.checked)}
                        />
                        ${area} (${entities.length})
                      </summary>
                      <table class="entity-table">
                        <thead>
                          <tr>
                            <th class="select-col"></th>
                            <th>Device</th>
                            <th>Name</th>
                            <th>Entity ID</th>
                          </tr>
                        </thead>
                        <tbody>
                          ${entities.map(entity => html`
                            <tr class="${this.selectedEntities.some(e => e.entity_id === entity.entity_id) ? 'selected' : ''}">
                              <td>
                                <input
                                  type="checkbox"
                                  ?checked=${this.selectedEntities.some(e => e.entity_id === entity.entity_id)}
                                  @change=${() => this.toggleSelectEntity(entity)}
                                />
                              </td>
                              <td>${entity.device_name}</td>
                              <td>${entity.name}</td>
                              <td>${entity.entity_id}</td>
                            </tr>
                          `)}
                        </tbody>
                      </table>
                    </details>
                  `)
              }
            </div>

            <div class="actions">
              <span>${this.selectedEntities.length} entities selected</span>
              <div class="button-highlight-message">
                <strong>This is the "Get ID Suggestions" button ↓</strong>
              </div>
              <button
                class="primary get-suggestions-highlight"
                ?disabled=${this.selectedEntities.length === 0 || this.suggestionsLoading}
                @click=${this.getSuggestions}
              >
                ${this.suggestionsLoading
                  ? html`
                      <ha-circular-progress active size="small"></ha-circular-progress>
                      Getting suggestions...
                    `
                  : "Get ID Suggestions"}
              </button>
            </div>

            ${this.suggestions.length > 0 ? html`
              <div class="suggestions-section">
                <h3>Suggested Entity IDs</h3>
                <div class="suggestions-table-container">
                  <table class="suggestions-table">
                    <thead>
                      <tr>
                        <th>Area</th>
                        <th>Device</th>
                        <th>Current Name</th>
                        <th>Suggested Entity ID</th>
                        <th>Suggested Friendly Name</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${this.suggestions.map(suggestion => html`
                        <tr>
                          <td>${suggestion.area_name}</td>
                          <td>${suggestion.device_name}</td>
                          <td>${suggestion.name}</td>
                          <td>${suggestion.suggested_id}</td>
                          <td>${suggestion.suggested_name}</td>
                          <td>
                            <button
                              class="apply-button"
                              @click=${() =>
                                this.applyRename(
                                  suggestion,
                                  suggestion.suggested_id,
                                  suggestion.suggested_name
                                )}
                            >
                              Apply
                            </button>
                          </td>
                        </tr>
                      `)}
                    </tbody>
                  </table>
                </div>
                <div class="apply-all">
                  <button
                    class="primary"
                    @click=${this.applyAllSuggestions}
                  >
                    Apply All Suggestions
                  </button>
                </div>
              </div>
            ` : ""}
          `}
        </div>
      </ha-card>
    `;
  }

  static get styles() {
    return css`
      :host {
        display: block;
        padding: 16px;
        font-family: var(--primary-font-family, "Roboto", "system-ui", "sans-serif");
      }

      ha-card {
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
      }

      .card-content {
        padding: 16px;
      }

      .message {
        padding: 10px;
        margin-bottom: 16px;
        border-radius: 4px;
      }

      .message.error {
        background-color: #FFF5F5;
        color: #C53030;
        border: 1px solid #FEB2B2;
      }

      .message.success {
        background-color: #F0FFF4;
        color: #276749;
        border: 1px solid #C6F6D5;
      }

      .message.warning {
        background-color: #FFFAF0;
        color: #C05621;
        border: 1px solid #FEEBC8;
      }

      .message.info {
        background-color: #EBF8FF;
        color: #2C5282;
        border: 1px solid #BEE3F8;
      }

      .filters {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-bottom: 16px;
      }

      .search-box {
        display: flex;
        align-items: center;
        flex: 1;
        min-width: 200px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        padding: 0 8px;
      }

      .search-box input {
        flex: 1;
        border: none;
        padding: 8px;
        background: transparent;
        color: var(--primary-text-color);
      }

      .filter-selects {
        display: flex;
        gap: 8px;
      }

      .filter-selects select {
        padding: 8px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
        background: var(--card-background-color, white);
        color: var(--primary-text-color);
      }

      .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 32px;
      }

      .entity-table-container, .suggestions-table-container {
        overflow-x: auto;
        margin-bottom: 16px;
      }

      table {
        width: 100%;
        border-collapse: collapse;
      }

      th, td {
        text-align: left;
        padding: 8px 16px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
      }

      th {
        font-weight: 500;
        background-color: var(--secondary-background-color, #f5f5f5);
      }

      tr.selected {
        background-color: var(--light-primary-color, #D1E3FF);
      }

      .select-col {
        width: 50px;
      }

      .no-entities {
        text-align: center;
        padding: 32px;
        color: var(--secondary-text-color);
      }

      .select-all-row {
        display: flex;
        align-items: center;
        padding: 8px 16px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
      }

      .select-all-row input {
        margin-right: 8px;
      }

      .area-group {
        margin-bottom: 8px;
      }

      .area-group summary {
        display: flex;
        align-items: center;
        cursor: pointer;
        padding: 8px 16px;
        background: var(--secondary-background-color, #f5f5f5);
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 4px;
      }

      .area-group summary input {
        margin-right: 8px;
      }

      .actions {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
        border: 2px dashed #03a9f4;
        background: #e3f2fd;
        padding: 16px;
        margin-top: 16px;
        margin-bottom: 24px;
      }

      .button-highlight-message {
        color: #01579b;
        background: #b3e5fc;
        padding: 4px 8px;
        border-radius: 4px;
        margin-bottom: 4px;
        font-size: 1em;
      }

      .get-suggestions-highlight {
        border: 2px solid #0288d1;
        background: #03a9f4;
        color: #fff;
        font-size: 1.2em;
        font-weight: bold;
        box-shadow: 0 2px 12px rgba(2,136,209,0.15);
        margin-top: 4px;
      }

      button {
        cursor: pointer;
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        background-color: var(--secondary-background-color, #f5f5f5);
        color: var(--primary-text-color, #212121);
        font-family: inherit;
        transition: background 0.2s, color 0.2s;
      }

      button.primary {
        background-color: var(--primary-color, #03a9f4);
        color: var(--text-primary-color, #fff);
        font-size: 1.1em;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      }

      button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .apply-button {
        background-color: var(--primary-color, #03a9f4);
        color: var(--text-primary-color, #fff);
        padding: 4px 8px;
        font-size: 0.9em;
      }

      .suggestions-section {
        margin-top: 24px;
        border-top: 1px solid var(--divider-color, #e0e0e0);
        padding-top: 16px;
      }

      .suggestions-section h3 {
        margin-top: 0;
        margin-bottom: 16px;
      }

      .apply-all {
        display: flex;
        justify-content: flex-end;
        margin-top: 16px;
      }
    `;
  }
}

customElements.define("entity-renamer-panel", EntityRenamerPanel);

class EntityRenamerPanelElement extends HTMLElement {
  constructor() {
    super();
    this._shadowRoot = this.attachShadow({ mode: "open" });
    this._shadowRoot.innerHTML = `
      <entity-renamer-panel></entity-renamer-panel>
    `;
  }

  set hass(hass) {
    const panel = this._shadowRoot.querySelector("entity-renamer-panel");
    panel.hass = hass;
  }

  setProperties(properties) {
    const panel = this._shadowRoot.querySelector("entity-renamer-panel");
    if (panel) {
      for (const [key, value] of Object.entries(properties)) {
        panel[key] = value;
      }
    }
  }
}

customElements.define("entity-renamer-panel-element", EntityRenamerPanelElement);
