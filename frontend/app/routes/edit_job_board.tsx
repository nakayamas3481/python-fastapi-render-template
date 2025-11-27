import { Form, Link, redirect, useLoaderData } from "react-router";
import type { Route } from "../+types/root";
import { Field, FieldGroup, FieldLabel, FieldLegend } from "~/components/ui/field";
import { Input } from "~/components/ui/input";
import { Button } from "~/components/ui/button";
import JobBoards from "./job-boards";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const res = await fetch(`/api/job-boards/${params.jobBoardId}`);
  const jobBoard = await res.json();
  return { jobBoard };
}

export default function EditJobBoardForm(_: Route.ComponentProps) {
  return (
    <div className="w-full max-w-md">
      <Form method="post" encType="multipart/form-data">
        <FieldGroup>
          <FieldLegend>Edit Job Board</FieldLegend>
          <Field>
            <FieldLabel htmlFor="slug">
              Slug
            </FieldLabel>
            <Input
              id="slug"
              name="slug"
              placeholder="acme"
              required
            />
          </Field>
          <Field>
            <FieldLabel htmlFor="logo">
              Logo
            </FieldLabel>
            <Input
              id="logo"
              name="logo"
              type="file"
              required
            />
          </Field>
          <div className="float-right">
            <Field orientation="horizontal">
              <Button type="submit">Submit</Button>
              <Button variant="outline" type="button">
                <Link to="/job-boards">Cancel</Link>
              </Button>
            </Field>
          </div>
        </FieldGroup>
      </Form>
    </div>
  );
}

export async function clientAction({ request, params }: Route.ClientActionArgs) {
    const formData = await request.formData()
    await fetch(`/api/job-boards/${params.jobBoardId}`, {
        method: 'PUT',
        body: formData,
    })
    return redirect('/job-boards')
}
