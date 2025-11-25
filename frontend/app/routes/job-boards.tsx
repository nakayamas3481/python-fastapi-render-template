import { Link } from "react-router";

export async function clientLoader() {
  const res = await fetch(`/api/job-boards`);
  const jobBoards = await res.json();
  return {jobBoards}
}

export default function JobBoards({loaderData}) {
  return (
    <div>
      {loaderData.jobBoards.map(
        (jobBoard) => 
          <p key={jobBoard.id}>
            <Link to={`/job-boards/${jobBoard.id}/job-posts`}>{jobBoard.slug}</Link>
            {jobBoard. logo_url
              ? <img src={jobBoard.logo_url}></img>
              : <></>
            }
          </p>
      )}
    </div>
  )
}