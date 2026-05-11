# Logos LIP Index

An IETF-style index of Logos-managed LIPs across Storage, Messaging, Blockchain,
AnonComms, and Research sections. Use the filters below to jump straight to a
specification.

<div class="landing-hero">
  <div class="filter-row">
    <input id="rfc-search" type="search" placeholder="Search by number, title, status, component..." aria-label="Search LIPs">
    <div class="chips" id="status-chips">
      <span class="chip active" data-status="current" data-label="Current">Current</span>
      <span class="chip" data-status="all" data-label="All">All</span>
      <span class="chip" data-status="stable" data-label="Stable">Stable</span>
      <span class="chip" data-status="draft" data-label="Draft">Draft</span>
      <span class="chip" data-status="raw" data-label="Raw">Raw</span>
      <span class="chip" data-status="deprecated" data-label="Deprecated">Deprecated</span>
      <span class="chip" data-status="deleted" data-label="Deleted">Deleted</span>
    </div>
  </div>
  <div class="filter-row">
    <div class="chips" id="component-chips">
      <span class="chip active" data-component="all" data-label="All components">All components</span>
      <span class="chip" data-component="messaging" data-label="Messaging">Messaging</span>
      <span class="chip" data-component="blockchain" data-label="Blockchain">Blockchain</span>
      <span class="chip" data-component="storage" data-label="Storage">Storage</span>
      <span class="chip" data-component="anoncomms" data-label="AnonComms">AnonComms</span>
      <span class="chip" data-component="research" data-label="Research">Research</span>
    </div>
  </div>
  <div class="filter-row">
    <div class="chips" id="date-chips">
      <span class="chip active" data-date="all" data-label="All time">All time</span>
      <span class="chip" data-date="latest" data-label="Latest" data-count="false">Latest</span>
      <span class="chip" data-date="last90" data-label="Last 90 days">Last 90 days</span>
    </div>
  </div>
</div>

<div class="results-row">
  <div id="results-count" class="results-count">Loading RFC index...</div>
  <div class="results-hint">Click a column to sort</div>
</div>

<div id="rfc-table-container" class="table-wrap"></div>

<noscript>
  <p class="noscript-note">JavaScript is required to load the RFC index table.</p>
</noscript>
