# Module delete_posted_journal_entries
All the changes this project will be documented in this file.

## Update Module Version 14 || 05-07-2021

### Module Account Move

#### CREATE
- New Method [superunlink()]
  - change account status from published to draft
  - if account reconcile exist, remove reconcile
#### UPDATE
- Method unlink():
  - add user permission , if the user have permission apply superunlink()

