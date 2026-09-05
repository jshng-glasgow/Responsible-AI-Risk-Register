# Workshop mode maintainer runbook

Workshop mode lets issue-form submissions update the default branch without
opening pull requests. It is intended for facilitated events where maintainers
are actively monitoring submissions.

## Enable workshop mode

1. Open the repository's **Settings** page.
2. Go to **Secrets and variables** > **Actions** > **Variables**.
3. Set `WORKSHOP_AUTO_PUBLISH_NEW_RISKS` to `true`.

Despite its historical name, this variable controls direct publishing for
issues labelled `new risk`, `risk update`, and `new resource`.

When workshop mode is enabled:

- `new risk` issues append a risk directly to `register/risks.csv`;
- `risk update` issues update the referenced risk directly; and
- `new resource` issues append a resource directly to `resources/resources.csv`.

These changes bypass pull-request review. The workflows regenerate and deploy
the public site after publishing.

## Monitor the workshop

Monitor the repository's **Actions** page for failed or cancelled issue
workflows. Risk additions and updates share the `csv-update` concurrency group,
which runs one workflow at a time and queues up to 100 pending runs. Resource
submissions use a separate concurrency group.

If a submission fails or is cancelled:

1. Check that the submitted issue identifies a valid risk and contains valid
   field values.
2. Correct the issue if necessary.
3. Remove and reapply its automation label (`new risk`, `risk update`, or
   `new resource`) to trigger the workflow again.

Before retrying a failed direct publication, confirm that the issue has not
already been recorded in the relevant CSV.

## Disable workshop mode

After the workshop, change `WORKSHOP_AUTO_PUBLISH_NEW_RISKS` to any value other
than `true`, or delete the variable. New submissions will then return to the
normal pull-request workflow.
