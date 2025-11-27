import { type RouteConfig, layout, route } from "@react-router/dev/routes";

export default [
    layout("layout/default.tsx",[
        route("/", "routes/home.tsx"),
        route("job-boards", "routes/job-boards.tsx"),
        route("job-boards/:jobBoardId/job-posts", "routes/job_posts.tsx"),
        route("job-boards/new", "routes/new_job_board.tsx"),
        route("job-boards/:jobBoardId/edit", "routes/edit_job_board.tsx")
    ])
] satisfies RouteConfig;
