import { Link, useFetcher } from "react-router";
import { Avatar, AvatarImage } from "~/components/ui/avatar";
import { Button } from "~/components/ui/button";
import {
  Table, TableBody, TableCell, TableHead,
  TableHeader, TableRow
} from "~/components/ui/table";

export async function clientLoader() {
  const res = await fetch(`/api/job-boards`);
  const jobBoards = await res.json();
  return { jobBoards };
}

export default function JobBoards({ loaderData }) {
  const fetcher = useFetcher();
  return (
    <div className="min-h-screen bg-background">
      {/* ページ全体のコンテナ */}
      <div className="mx-auto max-w-5xl px-6 py-10">
        
        {/* ヘッダー（企業っぽさの要） */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">
              Job Boards
            </h1>
          </div>
          {/* 右上に何か置く想定（あとで検索やボタン追加できる） */}
          <div className="text-sm text-muted-foreground">
              <Button>
                <Link to="/job-boards/new">Add New Job Board</Link>
              </Button>
          </div>
        </div>

        {/* カード（中身を“製品っぽく”見せる枠） */}
        <div className="rounded-xl border bg-card shadow-sm">
          <Table className="w-full">
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead className="w-28">Logo</TableHead>
                <TableHead>Company</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {loaderData.jobBoards.map((jobBoard) => (
                <TableRow key={jobBoard.id} className="h-16">
                  <TableCell className="align-middle">
                    {jobBoard.logo_url ? (
                      <Avatar className="h-9 w-9">
                        <AvatarImage src={jobBoard.logo_url} />
                      </Avatar>
                    ) : null}
                  </TableCell>

                  <TableCell className="align-middle">
                    <Link
                      to={`/job-boards/${jobBoard.id}/job-posts`}
                      className="capitalize font-medium hover:underline"
                    >
                      {jobBoard.slug}
                    </Link>
                  </TableCell>
                  <TableCell className="align-middle">
                      <Button variant="outline" size="sm" asChild>
                        <Link to={`/job-boards/${jobBoard.id}/edit`}>Edit</Link>
                      </Button>
                  </TableCell>
                  <TableCell className="align-middle">
                    <fetcher.Form method="post"
                      onSubmit={(event) => {
                      const response = confirm(
                        `Please confirm you want to delete this job board '${jobBoard.slug}'.`,
                      );
                      if (!response) {
                        event.preventDefault();
                      }
                    }}>
                      <input name="job_board_id" type="hidden" value={jobBoard.id}></input>
                      <button>Delete</button>
                    </fetcher.Form>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

      </div>
    </div>
  );
}

export async function clientAction({ request}: Route.ClientActionArgs) {
  const formData = await request.formData()
  const jobBoardId = formData.get('job_board_id')
  await fetch(`/api/job-boards/${jobBoardId}`, {
    method: 'DELETE',
  })
}
